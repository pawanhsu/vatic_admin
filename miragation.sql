ALTER TABLE `users`
	ADD COLUMN `forgetPasswordToken` VARCHAR(50) NULL DEFAULT NULL AFTER `verification`,
	ADD COLUMN `forgetPasswordTokenExpireTime` DATETIME NULL DEFAULT NULL AFTER `forgetPasswordToken`,
	DROP PRIMARY KEY,
	ADD PRIMARY KEY (`id`),
	ADD UNIQUE INDEX `username` (`username`);

ALTER TABLE `users`
	CHANGE COLUMN `token` `token` VARCHAR(50) NULL AFTER `priority`;

UPDATE `users` 
	SET `token` = null WHERE `token` = "";

LTER TABLE `users`
	ADD UNIQUE INDEX `token` (`token`);
