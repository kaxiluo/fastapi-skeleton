/*
* 创建用户表users
*/
CREATE TABLE `users` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `username` varchar(255) CHARACTER SET utf8 NOT NULL COMMENT '用户名',
  `password` varchar(255) CHARACTER SET utf8 NOT NULL DEFAULT '' COMMENT '密码',
  `cellphone` varchar(45) CHARACTER SET utf8 DEFAULT NULL COMMENT '手机',
  `email` varchar(255) CHARACTER SET utf8 DEFAULT NULL COMMENT '邮箱',
  `email_verified_at` datetime DEFAULT NULL COMMENT '邮箱验证时间',
  `state` varchar(50) CHARACTER SET utf8 NOT NULL DEFAULT 'enabled' COMMENT '状态 enabled disabled',
  `nickname` varchar(255) CHARACTER SET utf8 NOT NULL DEFAULT '' COMMENT '昵称',
  `gender` varchar(10) CHARACTER SET utf8 NOT NULL DEFAULT 'unknown' COMMENT '性别 male，female',
  `avatar` varchar(255) CHARACTER SET utf8 NOT NULL DEFAULT '' COMMENT '头像',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `udx_username` (`username`),
  UNIQUE KEY `udx_cellphone` (`cellphone`),
  UNIQUE KEY `udx_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


/*
* 插入用户，密码均为123456
*/
INSERT  INTO `users`(`id`,`username`,`password`,`created_at`,`updated_at`) VALUES
(1,'fake_user1','$2b$12$qn3Hjh8zCfYsSnbqHBq63eXjaTwWs4r/SH3yLycDAOTFUi80em6Ju',NOW(),NOW()),
(2,'fake_user2','$2b$12$qn3Hjh8zCfYsSnbqHBq63eXjaTwWs4r/SH3yLycDAOTFUi80em6Ju',NOW(),NOW());