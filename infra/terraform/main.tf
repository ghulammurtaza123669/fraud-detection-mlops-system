resource "kubernetes_namespace" "fraud" {
  metadata {
    name = var.namespace
  }
}

resource "kubernetes_config_map" "api" {
  metadata {
    name      = "fraud-detection-config"
    namespace = kubernetes_namespace.fraud.metadata[0].name
  }

  data = {
    APP_NAME            = "fraud-detection-api"
    APP_ENV             = "production"
    LOG_LEVEL           = "INFO"
    MODEL_PATH          = "/app/models/fraud_model.joblib"
    MODEL_METADATA_PATH = "/app/models/model_metadata.json"
    FRAUD_THRESHOLD     = "0.50"
  }
}

resource "kubernetes_secret" "api" {
  metadata {
    name      = "fraud-detection-secret"
    namespace = kubernetes_namespace.fraud.metadata[0].name
  }

  data = {
    API_TOKEN_PLACEHOLDER = "replace-in-secret-manager"
  }

  type = "Opaque"
}

resource "kubernetes_deployment" "api" {
  metadata {
    name      = "fraud-detection-api"
    namespace = kubernetes_namespace.fraud.metadata[0].name
    labels = {
      app = "fraud-detection-api"
    }
  }

  spec {
    replicas = var.replicas

    selector {
      match_labels = {
        app = "fraud-detection-api"
      }
    }

    template {
      metadata {
        labels = {
          app = "fraud-detection-api"
        }
      }

      spec {
        container {
          name  = "api"
          image = var.image

          port {
            container_port = 8000
          }

          env_from {
            config_map_ref {
              name = kubernetes_config_map.api.metadata[0].name
            }
          }

          env_from {
            secret_ref {
              name = kubernetes_secret.api.metadata[0].name
            }
          }

          resources {
            limits = {
              cpu    = "1000m"
              memory = "1Gi"
            }
            requests = {
              cpu    = "250m"
              memory = "512Mi"
            }
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "api" {
  metadata {
    name      = "fraud-detection-api"
    namespace = kubernetes_namespace.fraud.metadata[0].name
    labels = {
      app = "fraud-detection-api"
    }
  }

  spec {
    selector = {
      app = "fraud-detection-api"
    }

    port {
      name        = "http"
      port        = 80
      target_port = 8000
    }
  }
}
