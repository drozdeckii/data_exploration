source("scripts/r/db.R")
con <- get_connection()
print(dbGetQuery(con, "SELECT version();"))
dbDisconnect(con)