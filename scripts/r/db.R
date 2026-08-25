library(DBI)

get_connection <- function() {
  dbConnect(
    RPostgres::Postgres(),
    host = Sys.getenv("DB_HOST", "localhost"),
    port = as.integer(Sys.getenv("DB_PORT", "5432")),
    dbname = Sys.getenv("DB_NAME", "sandbox_dev"),
    user = Sys.getenv("DB_USER", "postgres"),
    password = Sys.getenv("DB_PASSWORD")
  )
}
