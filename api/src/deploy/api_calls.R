get_predictions <- function(df) {
  
  # Convert df to JSON
  request_body_content <- df %>% 
    toJSON(auto_unbox = TRUE)
  
  # Calling the API
  result <- POST(
    paste0(config_file$URI, "/predict"),
    body = request_body_content,
    add_headers(.headers = c("Content-Type"="application/json"))
  )
  
  # Get result
  output <- content(result, as = 'text') %>% fromJSON() %>% as.data.table()
  
  return(output)
}

get_predictions_2 <- function(center_id, meal_id) {
  
  # Build the content with center_id and meal_id
  request_body_content <- list("center_id" = center_id, "meal_id" = meal_id) %>% 
    toJSON(auto_unbox = TRUE)
  
  print(request_body_content)
  
  # Calling the API
  result <- POST(
    paste0(config_file$URI, "/predict2"),
    body = request_body_content,
    add_headers(.headers = c("Content-Type"="application/json"))
  )
  
  # Get result
  output <- content(result, as = 'text') %>% fromJSON() %>% as.data.table()
  
  return(output)
}

train_model <- function(center_id, meal_id) {
  
  # Build the content with center_id and meal_id
  request_body_content <- list("center_id" = center_id, "meal_id" = meal_id) %>% 
    toJSON(auto_unbox = TRUE)
  
  # Calling the API
  result <- POST(
    paste0(config_file$URI, "/train"),
    body = request_body_content,
    add_headers(.headers = c("Content-Type"="application/json"))
  )
  
  # Get result
  output <- content(result)
  
  return(output)
}
