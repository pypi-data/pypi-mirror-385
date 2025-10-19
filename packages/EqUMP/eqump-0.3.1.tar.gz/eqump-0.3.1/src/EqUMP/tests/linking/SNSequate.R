library(SNSequate)
library(jsonlite)
data(KB36)
parm.x = KB36$KBformX_par
parm.y = KB36$KBformY_par
comitems = seq(3, 36, 3)
parm = as.data.frame(cbind(parm.y, parm.x))
obj <- irt.link(parm,comitems,model="3PL",icc="logistic",D=1.7)


# Prepare output
output <- list(
  mm = list(A=obj$mm[1], B=obj$mm[2]),
  ms = list(A=obj$ms[1], B=obj$ms[2]),
  hb = list(A=obj$Haebara[1], B=obj$Haebara[2]),
  sl = list(A=obj$StockLord[1], B=obj$StockLord[2])
)

cat(toJSON(output, auto_unbox = TRUE))