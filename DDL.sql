CREATE TABLE `user` (
  `id` varchar(20) NOT NULL,
  `createdAt` bigint NOT NULL,
  `seenAt` bigint DEFAULT NULL,
  `playtimeTotal` int NOT NULL,
  `url` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `tournament` (
  `id` varchar(20) NOT NULL,
  `startsAt` datetime NOT NULL,
  `system` varchar(45) NOT NULL,
  `fullName` varchar(45) NOT NULL,
  `key` varchar(45) NOT NULL,
  `clockLimit` int NOT NULL,
  `clockIncrement` int NOT NULL,
  `minutes` int NOT NULL,
  `variant` varchar(45) NOT NULL,
  `nbPlayers` int NOT NULL,
  `rated` tinyint NOT NULL,
  `headline` varchar(45) DEFAULT NULL,
  `berserkable` tinyint NOT NULL,
  `description` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `event` (
  `id` char(8) NOT NULL,
  `event` varchar(45) NOT NULL,
  `tournamentId` varchar(20) DEFAULT NULL,
  `whiteId` varchar(20) NOT NULL,
  `blackId` varchar(20) NOT NULL,
  `UTCDate` date NOT NULL,
  `UTCTime` time NOT NULL,
  `whiteElo` int NOT NULL,
  `blackElo` int NOT NULL,
  `whiteRatingDiff` int NOT NULL,
  `blackRatingDiff` int NOT NULL,
  `opening` varchar(100) NOT NULL,
  `timeControl` varchar(20) NOT NULL,
  `result` varchar(10) NOT NULL,
  `termination` varchar(100) NOT NULL,
  `moves` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `whiteId` (`whiteId`),
  KEY `blackId` (`blackId`),
  KEY `tournamentId` (`tournamentId`),
  CONSTRAINT `event_ibfk_1` FOREIGN KEY (`whiteId`) REFERENCES `user` (`id`),
  CONSTRAINT `event_ibfk_2` FOREIGN KEY (`blackId`) REFERENCES `user` (`id`),
  CONSTRAINT `event_ibfk_3` FOREIGN KEY (`tournamentId`) REFERENCES `tournament` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;