library(equateIRT)
library(jsonlite)

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1) stop("Usage: Rscript SL_onedirect.R <input_json_file>")
input <- fromJSON(args[1])

a_base <- as.numeric(input$a_base)
b_base <- as.numeric(input$b_base)
a_new  <- as.numeric(input$a_new)
b_new  <- as.numeric(input$b_new)

Dconst <- 1.702  # your choice

# Build beta parameterization for modIRT (2PL; no guessing column):
beta_base <- cbind(
  "beta.1i" = -(Dconst * a_base * b_base),
  "beta.2i" =  (Dconst * a_base)
)
beta_new <- cbind(
  "beta.1i" = -(Dconst * a_new * b_new),
  "beta.2i" =  (Dconst * a_new)
)

# All items common: identical names on both forms
stopifnot(nrow(beta_base) == nrow(beta_new))
common_names <- paste0("I", seq_len(nrow(beta_base)))
rownames(beta_base) <- common_names
rownames(beta_new)  <- common_names

mods <- modIRT(
  coef    = list(base = beta_base, new = beta_new),
  names   = c("base", "new"),
  display = FALSE
)

fit <- direc(
  mods = mods,
  which = c("base", "new"),
  method = "Stocking-Lord",
  D = Dconst,
  quadrature = TRUE,
  nq = 41
)

S <- summary(fit)$coefficients  # rows: A,B ; cols: Estimate, StdErr
# print(S)

out <- list(
  A    = unname(S["A", "Estimate"]),
  B    = unname(S["B", "Estimate"]),
  se_A = unname(S["A", "StdErr"]),
  se_B = unname(S["B", "StdErr"])
)

cat(toJSON(out, auto_unbox = TRUE))
