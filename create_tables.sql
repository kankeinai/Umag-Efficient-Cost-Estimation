create table IF NOT EXISTS sale
(
    id INTEGER  primary key AUTOINCREMENT,
    barcode   BIGINT   not null,
    quantity  int(11)  not null default 1,
    price     int(11)  not null default 0,
    sale_time datetime not null default current_timestamp,
    margin int(11)  not null default 0
);

create table IF NOT EXISTS supply
(
    id          INTEGER  primary key AUTOINCREMENT,
    barcode     BIGINT   not null,
    quantity    int(11)  not null default 1,
    price       int(11)  not null default 0,
    supply_time datetime not null default current_timestamp
);