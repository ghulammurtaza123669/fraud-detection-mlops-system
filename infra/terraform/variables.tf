variable "kubeconfig_path" {
  description = "Path to kubeconfig used by the Kubernetes provider."
  type        = string
  default     = "~/.kube/config"
}

variable "kube_context" {
  description = "Kubernetes context to deploy into."
  type        = string
  default     = null
}

variable "namespace" {
  description = "Namespace for fraud detection resources."
  type        = string
  default     = "fraud-detection"
}

variable "image" {
  description = "Container image for the fraud detection API."
  type        = string
  default     = "fraud-detection-api:latest"
}

variable "replicas" {
  description = "API replica count."
  type        = number
  default     = 3
}
