param (
    [string]$Option = 'Default'
)

$Global:ProjectNamespace = "project-healthy-reader"
$Global:ProjectRelease = "healthy-reader"

function Log-Message {
    param (
        [string]$Message
    )
    Write-Host "$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss')) - $Message"
}

# -----------------------------
# Clean functions
# -----------------------------
function Invoke-Clean {
    Log-Message "Running clean option..."
    Invoke-DockerClean
    Invoke-KubernetesClean
}

function Invoke-DockerClean {
    Log-Message "Cleaning Docker resources..."
    docker-compose --env-file ./config/.env.dev down --volumes
    docker volume prune -f
    docker image prune -a -f
}

function Invoke-KubernetesClean {
    Log-Message "Cleaning Kubernetes resources..."

    kubectl delete deployment --all
    kubectl delete service --all

    helm uninstall $Global:ProjectRelease -n $Global:ProjectNamespace --ignore-not-found
    kubectl delete namespace $Global:ProjectNamespace

    kubectl delete cronjob update-recommendations

}

# -----------------------------
# Docker functions
# -----------------------------
function Invoke-DockerBuild {
    Log-Message "Building Docker images..."
    docker-compose --env-file ./config/.env.dev build
}

function Invoke-DockerStart {
    Log-Message "Starting Docker containers..."
    docker-compose --env-file ./config/.env.dev up -d
}

function Invoke-DockerInitJobs {
    Log-Message "Running one-off init jobs..."
    docker-compose --env-file ./config/.env.dev run --rm user-service python manage.py migrate
    docker-compose --env-file ./config/.env.dev run --rm user-service python manage.py import_users

    docker-compose --env-file ./config/.env.dev run --rm book-service python manage.py migrate
    docker-compose --env-file ./config/.env.dev run --rm book-service python manage.py import_books

    docker-compose --env-file ./config/.env.dev run --rm rating-service python manage.py migrate
    docker-compose --env-file ./config/.env.dev run --rm rating-service python manage.py import_ratings
}


function Invoke-DockerCleanBuildStart {
    Log-Message "Cleaning resources, building and starting Docker containers..."
    Invoke-Clean
    Invoke-DockerBuild
    # Invoke-DockerInitJobs
    Invoke-DockerStart
}

function Invoke-DockerStop {
    Log-Message "Stopping Docker containers..."
    docker-compose --env-file ./config/.env.dev stop
}

function Invoke-DockerRestart {
    Log-Message "Retarting Docker containers..."
    Invoke-DockerStop
    Invoke-DockerStart
}

# -----------------------------
# Kubernetes functions
# -----------------------------
function Invoke-KubernetesCleanBuildStart {
    Log-Message "Cleaning resources, building Docker images, and starting Kubernetes resources..."
    Invoke-Clean
    Invoke-DockerBuild

    # Ensure namespace exists
    kubectl get namespace $Global:ProjectNamespace -o name 2>$null
    if ($LASTEXITCODE -ne 0) {
        kubectl create namespace $Global:ProjectNamespace
    }

    # Config (in namespace)
    kubectl delete secret config-env-dev -n $Global:ProjectNamespace --ignore-not-found
    kubectl create secret generic config-env-dev -n $Global:ProjectNamespace --from-env-file=".\config\.env.dev"

    # Database init (only for recommendation service here)
    kubectl delete configmap recommendation-init -n $Global:ProjectNamespace --ignore-not-found
    kubectl create configmap recommendation-init -n $Global:ProjectNamespace --from-file=./services/recommendation-service/db/init.sql

    # TLS Secret
    kubectl delete secret app-tls-secret -n $Global:ProjectNamespace --ignore-not-found
    kubectl create secret tls app-tls-secret -n $Global:ProjectNamespace --key tls.key --cert tls.crt

    # Ingress-NGINX (lives in its own namespace, don’t override it)
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.1/deploy/static/provider/cloud/deploy.yaml

    # Deploy Helm chart (upgrade or install)
    helm upgrade --install $Global:ProjectRelease ./k8s -n $Global:ProjectNamespace

    # Verify rollout
    kubectl get all -n $Global:ProjectNamespace
}

# -----------------------------
# Main switch
# -----------------------------
switch ($Option) {
    'Clean' { Invoke-Clean }
    'Docker' { Invoke-DockerCleanBuildStart }
    'Kubernetes' { Invoke-KubernetesCleanBuildStart }
    'DockerStart' { Invoke-DockerStart }
    'DockerStop' { Invoke-DockerStop }
    'DockerRestart' { Invoke-DockerRestart }
    default { Log-Message "Invalid option: $Option" }
}
