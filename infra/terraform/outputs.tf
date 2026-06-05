output "namespace" {
  value = kubernetes_namespace.fraud.metadata[0].name
}

output "service_name" {
  value = kubernetes_service.api.metadata[0].name
}
