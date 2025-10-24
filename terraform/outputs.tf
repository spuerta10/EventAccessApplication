output "db_host" { # db public IP
    value = google_sql_database_instance.main.public_ip_address
}

output "cloud_run_service_url" {
    value = google_cloud_run_service.event-access-cloud-run.status[0].url
}