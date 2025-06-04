LOAD DATA INFILE 'C:/dara/database/pengaduan_detail.csv'
INTO TABLE pengaduan_detail
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n' -- Sesuaikan dengan format baris di file Anda
IGNORE 1 ROWS;
