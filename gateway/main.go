package main

import (
	"log"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"
	"strings"

	"github.com/joho/godotenv"
)

const apiPrefix = "/api/v1"

var (
	authPrefix            = apiPrefix + "/auth/"
	usersPrefix           = apiPrefix + "/users/"
	booksPrefix           = apiPrefix + "/books/"
	quotesPrefix          = apiPrefix + "/quotes/"
	authorsPrefix         = apiPrefix + "/authors/"
	tagsPrefix            = apiPrefix + "/tags/"
	ratingsPrefix         = apiPrefix + "/ratings/"
	recommendationsPrefix = apiPrefix + "/recommendations/"
	rootPrefix            = "/" // frontend
)

func main() {
	runningInDocker := os.Getenv("RUNNING_IN_DOCKER") == "true"

	if !runningInDocker {
		if err := godotenv.Load("./../config/.env.dev"); err != nil {
			log.Fatalf("Error loading .env.dev file: %v", err)
		}
	}

	// Select URLs based on environment
	userURL := getURL("USER_URL", runningInDocker)
	authURL := getURL("AUTH_URL", runningInDocker)
	bookURL := getURL("BOOK_URL", runningInDocker)
	quoteURL := getURL("QUOTE_URL", runningInDocker)
	authorURL := getURL("AUTHOR_URL", runningInDocker)
	tagURL := getURL("TAG_URL", runningInDocker)
	ratingURL := getURL("RATING_URL", runningInDocker)
	recommendationURL := getURL("RECOMMENDATION_URL", runningInDocker)
	frontendURL := getURL("FRONTEND_URL", runningInDocker)

	mux := http.NewServeMux()
	mux.Handle(authPrefix, reverseProxy(authURL, authPrefix))
	mux.Handle(usersPrefix, reverseProxy(userURL, usersPrefix))
	mux.Handle(booksPrefix, reverseProxy(bookURL, booksPrefix))
	mux.Handle(quotesPrefix, reverseProxy(quoteURL, quotesPrefix))
	mux.Handle(authorsPrefix, reverseProxy(authorURL, authorsPrefix))
	mux.Handle(tagsPrefix, reverseProxy(tagURL, tagsPrefix))
	mux.Handle(ratingsPrefix, reverseProxy(ratingURL, ratingsPrefix))
	mux.Handle(recommendationsPrefix, reverseProxy(recommendationURL, recommendationsPrefix))
	mux.Handle(rootPrefix, reverseProxy(frontendURL, rootPrefix))

	log.Println("API Gateway listening on :8080")

	if err := http.ListenAndServe(":8080", mux); err != nil {
		log.Fatalf("Gateway failed: %v", err)
	}

}

func getURL(urlName string, docker bool) string {
	var urlStr string
	if docker {
		urlStr = os.Getenv("DOCKER_" + urlName)
	} else {
		urlStr = os.Getenv("LOCAL_" + urlName)
	}

	if urlStr == "" {
		log.Fatalf("Environment variable for %s is not set", urlName)
	}
	return urlStr
}

func reverseProxy(target, prefix string) http.Handler {
	log.Printf("reverseProxy: %s", target)
	targetURL, err := url.Parse(target)
	if err != nil {
		log.Fatalf("Could not parse target URL %s: %v", target, err)
	}

	proxy := httputil.NewSingleHostReverseProxy(targetURL)

	originalDirector := proxy.Director
	proxy.Director = func(req *http.Request) {
		originalDirector(req)
		if prefix != "/" {
			req.URL.Path = "/" + strings.TrimPrefix(req.URL.Path, prefix)
		}
	}

	return proxy
}
