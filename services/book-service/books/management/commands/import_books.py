import csv
import json
import os
import re
import unicodedata
from typing import Dict, List, Tuple

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count

from books.models import Book, Author, Quote, Tag
from config.settings import BASE_DIR
from django_common.utils.isbn_helpers import *


# -----------------------------
# Normalization & validation
# -----------------------------
_INITIALS_RE = re.compile(r"\b([A-Za-z])\.(\s+)?(?=[A-Za-z])")
_PUNCT_SPACE_RE = re.compile(r"[,\u2010\u2011\u2012\u2013\u2014\u2015]+")  # commas & dashes
_MULTI_SPACE_RE = re.compile(r"\s+")
_ALLOWED_NAME_RE = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ' .\-]+$")

def strip_diacritics(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ASCII", "ignore").decode("utf-8")

def smart_title(s: str) -> str:
    # Title-case but preserve common particles and all-caps acronyms
    particles = {"de", "del", "la", "le", "van", "von", "der", "da", "dos", "du", "of"}
    words = s.split()
    out = []
    for i, w in enumerate(words):
        w2 = w
        if len(w) <= 3 and w.isupper():  # treat acronyms like "USA"
            w2 = w
        elif w.lower() in particles and i not in (0, len(words)-1):
            w2 = w.lower()
        else:
            w2 = w.capitalize()
        out.append(w2)
    return " ".join(out)

def normalize_author_display(name: str) -> str:
    """
    Produce a nice, human display name:
      - trim
      - collapse punctuation & spaces
      - insert space after each initial if missing: 'A.A.' -> 'A. A.'
      - title-case smartly
    """
    if not name:
        return "Unknown"

    name = name.strip()
    name = _PUNCT_SPACE_RE.sub(" ", name)
    name = _MULTI_SPACE_RE.sub(" ", name)

    # Add space after initials if missing, e.g., "A.A." -> "A. A."
    # This handles initials at the start of a word
    name = re.sub(r"\b([A-Z])\.(?=[A-Z])", r"\1. ", name)

    # Collapse multiple spaces again just in case
    name = _MULTI_SPACE_RE.sub(" ", name)

    name = smart_title(name)
    return name

def canonical_author_key(name: str) -> str:
    """
    Canonical key for matching/dedup:
      - ASCII fold
      - lowercase
      - remove all punct/spaces
    Example: "A. A. Attanasio" -> "aaattanasio"
    """
    ascii_name = strip_diacritics(name)
    ascii_name = ascii_name.lower()
    ascii_name = re.sub(r"[^a-z]", "", ascii_name)
    return ascii_name

def is_reasonable_author_name(name: str) -> bool:
    """Reject empty, numeric-only, or garbage names."""
    if not name or len(name.strip()) < 2:
        return False
    s = name.strip()
    if s.isdigit():
        return False
    if not _ALLOWED_NAME_RE.match(s):
        return False
    # too few alphabetics?
    if sum(ch.isalpha() for ch in s) < 2:
        return False
    return True

# -----------------------------
# Management command
# -----------------------------
BULK_CHUNK = 5000

class Command(BaseCommand):
    help = "Import books (books.csv) and quotes (quotes_01.jsonl), normalize & deduplicate authors."

    def handle(self, *args, **kwargs):
        self.import_books()
        self.import_quotes("quotes_01.jsonl")
        self.import_quotes("quotes_02.json")
        self.import_quotes("quotes_03.jsonl")

        # Deduplicate authors by canonical key
        self.deduplicate_authors()

        # ✅ Final totals
        self.stdout.write(self.style.SUCCESS(f"Total authors in database: {Author.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"Total books in database:   {Book.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"Total quotes in database:  {Quote.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"Total tags in database:    {Tag.objects.count()}"))

    # ------------------------
    # BOOKS
    # ------------------------
    def import_books(self):
        file_path = os.path.join(BASE_DIR, "data/books.csv")
        self.stdout.write(f"📚 Loading books from {file_path}")

        # Preload caches
        authors_by_name: Dict[str, Author] = {a.name: a for a in Author.objects.all()}
        authors_by_key: Dict[str, Author] = {canonical_author_key(a.name): a for a in Author.objects.all()}

        new_authors_batch: List[Author] = []
        books_batch: List[Book] = []

        # 1) Read CSV
        with open(file_path, newline="", encoding="latin-1") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=";")
            for row in reader:
                try:
                    isbn = clean_isbn(row["ISBN"])
                    if not is_valid_isbn(isbn):
                        continue

                    raw_author = (row.get("Book-Author") or "").strip('"').strip("'").strip()
                    display_name = normalize_author_display(raw_author)
                    if not is_reasonable_author_name(display_name):
                        continue

                    key = canonical_author_key(display_name)
                    author = authors_by_key.get(key)
                    if author is None:
                        # Create placeholder Author in-memory; defer DB write
                        author = Author(name=display_name, bio="")
                        new_authors_batch.append(author)
                        # Reserve the key to avoid duplicating in the same run
                        authors_by_key[key] = author

                    title = (row.get("Book-Title") or "").strip('"').strip("'")
                    year = row.get("Year-Of-Publication") or ""
                    year = int(year) if str(year).isdigit() else None

                    book = Book(
                        isbn=isbn,
                        title=title,
                        author=author,  # may be unsaved yet; resolved after bulk_create
                        year_of_publication=year,
                        publisher=(row.get("Publisher") or "").strip('"').strip("'"),
                        image_url_s=(row.get("Image-URL-S") or "").strip('"').strip("'"),
                        image_url_m=(row.get("Image-URL-M") or "").strip('"').strip("'"),
                        image_url_l=(row.get("Image-URL-L") or "").strip('"').strip("'"),
                    )
                    books_batch.append(book)
                except Exception:
                    # swallow bad rows silently or log if you prefer
                    continue

        # 2) Persist in chunks inside a transaction
        with transaction.atomic():
            if new_authors_batch:
                # save authors
                for i in range(0, len(new_authors_batch), BULK_CHUNK):
                    Author.objects.bulk_create(new_authors_batch[i:i+BULK_CHUNK], ignore_conflicts=True)

                # refresh caches (resolve actual DB instances by name)
                saved_names = [a.name for a in new_authors_batch]
                for a in Author.objects.filter(name__in=saved_names):
                    authors_by_name[a.name] = a
                    authors_by_key[canonical_author_key(a.name)] = a

            # resolve FK Author objects and bulk_create books
            resolved_books: List[Book] = []
            for b in books_batch:
                # If b.author is an unsaved instance with just a name, resolve to DB instance
                if not getattr(b.author, "pk", None):
                    resolved = authors_by_key[canonical_author_key(b.author.name)]
                    b.author = resolved
                resolved_books.append(b)

            if resolved_books:
                for i in range(0, len(resolved_books), BULK_CHUNK):
                    Book.objects.bulk_create(resolved_books[i:i+BULK_CHUNK], ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS(f"✅ Books imported. Total now: {Book.objects.count()}"))

    # ------------------------
    # QUOTES
    # ------------------------
    def import_quotes(self, filename):
        file_path = os.path.join(BASE_DIR, "data", filename)
        self.stdout.write(f"💬 Loading quotes from {file_path}")

        authors_by_key: Dict[str, Author] = {canonical_author_key(a.name): a for a in Author.objects.all()}
        tags_cache: Dict[str, Tag] = {t.name: t for t in Tag.objects.all()}

        new_authors_count = 0
        new_tags_count = 0
        new_quotes_count = 0
        
        def normalize_row(row: dict) -> dict:
            """Map different file formats to a common structure."""
            if "quote" in row:
                return {
                    "quote": (row.get("quote") or "").strip(),
                    "author": (row.get("author") or "Unknown").strip(),
                    "tags": row.get("tags") or [],
                }
            elif "Quote" in row:  # quotes_02.jsonl style
                return {
                    "quote": (row.get("Quote") or "").strip(),
                    "author": (row.get("Author") or "Unknown").strip(),
                    "tags": row.get("Tags") or [],
                }
            return {}

        with transaction.atomic():
            with open(file_path, "r", encoding="latin-1") as f:
                if filename.endswith(".jsonl"):
                    rows = (json.loads(line) for line in f)
                else:  # assume standard JSON array
                    rows = json.load(f)

                for raw_row in rows:
                    try:
                        row = normalize_row(raw_row)
                        if not row:
                            continue

                        display_name = normalize_author_display(row["author"])
                        if not is_reasonable_author_name(display_name):
                            continue

                        key = canonical_author_key(display_name)
                        author = authors_by_key.get(key)
                        if author is None:
                            author, created = Author.objects.get_or_create(
                                name=display_name, defaults={"bio": ""}
                            )
                            authors_by_key[key] = author
                            if created:
                                new_authors_count += 1

                        quote_text = row["quote"]
                        if not quote_text:
                            continue

                        quote, created = Quote.objects.get_or_create(
                            text=quote_text,
                            defaults={
                                "author": author,
                            },
                        )
                        if created:
                            new_quotes_count += 1
                        elif not quote.author_id:
                            quote.author = author
                            quote.save(update_fields=["author"])

                        # Tags
                        for tag_name in (row.get("tags") or []):
                            tag_name = tag_name.strip()
                            tag = tags_cache.get(tag_name)
                            if tag is None:
                                tag, created = Tag.objects.get_or_create(name=tag_name)
                                tags_cache[tag_name] = tag
                                if created:
                                    new_tags_count += 1
                            quote.tags.add(tag)

                    except Exception:
                        continue

        self.stdout.write(self.style.SUCCESS(f"✅ Imported {new_quotes_count} new quotes"))
        self.stdout.write(self.style.SUCCESS(f"➕ New authors created: {new_authors_count}"))
        self.stdout.write(self.style.SUCCESS(f"🏷️ New tags created: {new_tags_count}"))
   
    # ------------------------
    # DEDUP AUTHORS
    # ------------------------
    def deduplicate_authors(self):
        """
        Merge duplicate Author rows that normalize to the same canonical key.
        Prefer:
          1) The name with the most alphabetic characters (more complete).
          2) If tie, the longest name.
          3) If still tie, the earliest created id.
        Reassign all Book/Quote FKs, then delete duplicates.
        """
        self.stdout.write("🧹 Deduplicating authors...")
        authors = list(Author.objects.all().only("id", "name", "created_at"))
        buckets: Dict[str, List[Author]] = {}
        for a in authors:
            buckets.setdefault(canonical_author_key(a.name), []).append(a)

        merged = 0
        with transaction.atomic():
            for key, group in buckets.items():
                if len(group) <= 1:
                    continue

                # pick primary
                def score(a: Author) -> Tuple[int, int, int]:
                    letters = sum(ch.isalpha() for ch in a.name)
                    return (letters, len(a.name), -a.id)  # more letters, longer, older id wins

                group.sort(key=score, reverse=True)
                primary, *dups = group

                if not dups:
                    continue

                # Reassign FKs
                Book.objects.filter(author__in=dups).update(author=primary)
                Quote.objects.filter(author__in=dups).update(author=primary)

                # Delete duplicates
                Author.objects.filter(id__in=[d.id for d in dups]).delete()
                merged += len(dups)

        if merged:
            self.stdout.write(self.style.SUCCESS(f"🧩 Merged {merged} duplicate author record(s)."))
        else:
            self.stdout.write(self.style.SUCCESS("✅ No duplicate authors detected."))
