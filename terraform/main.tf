resource "google_sql_database_instance" "main" {
  name             = "${var.environment}-postgres"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = var.db_tier
    
    ip_configuration {
      ipv4_enabled = true  # enable public IP

      authorized_networks {
        name  = "allow-all"
        value = "0.0.0.0/0"
      }
    }
  }

  deletion_protection = false
}

resource "google_sql_database" "database" { # db creation
  name     = var.db_name
  instance = google_sql_database_instance.main.name
}

resource "google_sql_user" "user" { # db user creation
  name     = var.db_user
  instance = google_sql_database_instance.main.name
  password = var.db_password
}