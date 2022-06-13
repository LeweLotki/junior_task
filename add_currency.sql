USE `mydb`;

ALTER TABLE `mydb`.`product`
ADD `UnitPriceUSD` DECIMAL NOT NULL;
ALTER TABLE `mydb`.`product`
ADD `UnitPriceEuro` DECIMAL NOT NULL;
