# Cloud SQL 

resource "google_sql_database_instance" "main" { # create Cloud SQL instance
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

# Cloud Run

data "google_iam_policy" "event-access-noauth" { # Create public access
  binding {
    role = "roles/run.invoker"
    members = [
      "allUsers",
    ]
  }
}

# event access API
resource "google_cloud_run_service" "event-access-cloud-run" {  # deploy image to Cloud Run
  name     = "${var.environment}-${var.service_name}"
  location = var.region
  template {
    spec {
      containers {
        image = var.image_uri

        env {
            name  = "DB_HOST"
            value = google_sql_database_instance.main.public_ip_address
        }
        env {
            name  = "DB_PORT"
            value = "5432" # default Cloud SQL PostgreSQL port
        }
        env {
            name  = "DB_USER"
            value = google_sql_user.user.name
        }
        env {
            name  = "DB_PASSWORD"
            value = var.db_password
        }
        env {
            name  = "DB_NAME"
            value = google_sql_database.database.name
        }
      }
    }
  }
  traffic {
    percent         = 100
    latest_revision = true
  }
}

resource "google_cloud_run_service_iam_policy" "event-access-cloud-run-noauth" {  # enable public access on Cloud Run service
  location    = google_cloud_run_service.event-access-cloud-run.location
  project     = google_cloud_run_service.event-access-cloud-run.project
  service     = google_cloud_run_service.event-access-cloud-run.name
  policy_data = data.google_iam_policy.event-access-noauth.policy_data
}