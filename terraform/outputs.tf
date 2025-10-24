output "db_host" { # db public IP
    value = google_sql_database_instance.main.public_ip_address
}