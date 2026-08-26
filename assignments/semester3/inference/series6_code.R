fisher_scoring_mle <- function(x, tol = 1e-5, max_iter = 1000) {
  n <- length(x)
  theta_k <- mean(x) # Initial guess
  error <- Inf
  iter <- 0
  while(error > tol && iter < max_iter) {
    sum_term <- sum(1 / (1 + exp(x - theta_k)))
    theta_next <- theta_k + 3 - (6 / n) * sum_term
    
    error <- abs(theta_next - theta_k)
    theta_k <- theta_next
    iter <- iter + 1
  }
  if(iter == max_iter) {
    warning("Maximum iterations reached without convergence.")
  }
  return(list(mle = theta_k, iterations = iter))
}

## For theta = 0
t <- 0
sample_size <- 100
sample_0 <- rlogis(sample_size, t, 1)
fisher_scoring_mle(sample_0)



## Histograms for different number of samples
t <- 10 # theta = 10
num_sims <- 1000

# n = 100
sample_size <- 100
estimates <- c(num_sims)
for (i in 1:num_sims){
  sample_0 <- rlogis(sample_size, t, 1)
  estimates[i] = fisher_scoring_mle(sample_0)$mle
}
hist(estimates)

# n = 50
sample_size <- 50
estimates <- c(num_sims)
for (i in 1:num_sims){
  sample_0 <- rlogis(sample_size, t, 1)
  estimates[i] = fisher_scoring_mle(sample_0)$mle
}
hist(estimates)

# n = 200
sample_size <- 200
estimates <- c(num_sims)
for (i in 1:num_sims){
  sample_0 <- rlogis(sample_size, t, 1)
  estimates[i] = fisher_scoring_mle(sample_0)$mle
}
hist(estimates)

# n = 500
sample_size <- 500
estimates <- c(num_sims)
for (i in 1:num_sims){
  sample_0 <- rlogis(sample_size, t, 1)
  estimates[i] = fisher_scoring_mle(sample_0)$mle
}
hist(estimates)