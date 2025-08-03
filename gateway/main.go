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

func main() {
	runningInDocker := os.Getenv("RUNNING_IN_DOCKER") == "true"
	if !runningInDocker {
		if err := godotenv.Load("./../config/.env.dev"); err != nil {
			log.Fatalf("Error loading .env.dev file: %v", err)
		}
	}

	// Base URLs
	userService := getEnv("USER_SERVICE_URL")
	bookService := getEnv("BOOK_SERVICE_URL")
	ratingService := getEnv("RATING_SERVICE_URL")
	recommendationService := getEnv("RECOMMENDATION_SERVICE_URL")
	frontendService := getEnv("FRONTEND_URL")

	// Prefixes
	authPrefix := getEnv("AUTH_API_PREFIX") + "/"
	usersPrefix := getEnv("USER_API_PREFIX") + "/"
	booksPrefix := getEnv("BOOK_API_PREFIX") + "/"
	quotesPrefix := getEnv("QUOTE_API_PREFIX") + "/"
	authorsPrefix := getEnv("AUTHOR_API_PREFIX") + "/"
	tagsPrefix := getEnv("TAG_API_PREFIX") + "/"
	ratingsPrefix := getEnv("RATING_API_PREFIX") + "/"
	recommendationsPrefix := getEnv("RECOMMENDATION_API_PREFIX") + "/"

	mux := http.NewServeMux()
	mux.Handle(authPrefix, reverseProxy(userService+authPrefix, authPrefix))
	mux.Handle(usersPrefix, reverseProxy(userService+usersPrefix, usersPrefix))
	mux.Handle(booksPrefix, reverseProxy(bookService+booksPrefix, booksPrefix))
	mux.Handle(quotesPrefix, reverseProxy(bookService+quotesPrefix, quotesPrefix))
	mux.Handle(authorsPrefix, reverseProxy(bookService+authorsPrefix, authorsPrefix))
	mux.Handle(tagsPrefix, reverseProxy(bookService+tagsPrefix, tagsPrefix))
	mux.Handle(ratingsPrefix, reverseProxy(ratingService+ratingsPrefix, ratingsPrefix))
	mux.Handle(recommendationsPrefix, reverseProxy(recommendationService+recommendationsPrefix, recommendationsPrefix))

	// catch-all frontend
	mux.Handle("/", reverseProxy(frontendService, "/"))

	log.Println("API Gateway listening on :8080")
	if err := http.ListenAndServe(":8080", withCORS(mux)); err != nil {
		log.Fatalf("Gateway failed: %v", err)
	}
}

func getEnv(key string) string {
	val := os.Getenv(key)
	if val == "" {
		log.Fatalf("Environment variable %s not set", key)
	}
	return val
}

func reverseProxy(target string, prefix string) http.Handler {
	targetURL, err := url.Parse(target)
	if err != nil {
		log.Fatalf("Could not parse target URL %s: %v", target, err)
	}
	log.Printf("🔄 Proxying %s → %s", prefix, target)

	proxy := httputil.NewSingleHostReverseProxy(targetURL)
	originalDirector := proxy.Director

	proxy.Director = func(req *http.Request) {
		originalDirector(req)
		if prefix != "/" {
			req.URL.Path = "/" + strings.TrimPrefix(req.URL.Path, prefix)
		}
		req.Header.Set("X-Forwarded-Host", req.Host)
		req.Header.Set("X-Origin-Host", targetURL.Host)
	}

	return proxy
}

// withCORS is a simple CORS middleware
func withCORS(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		frontendOrigin := os.Getenv("FRONTEND_URL") // e.g. http://localhost:4200
		if frontendOrigin == "" {
			frontendOrigin = "*" // fallback
		}

		w.Header().Set("Access-Control-Allow-Origin", frontendOrigin)
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
		w.Header().Set("Access-Control-Allow-Credentials", "true")

		// Handle preflight request
		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusNoContent)
			return
		}

		next.ServeHTTP(w, r)
	})
}
