drop table if exists credentials;
create table credentials (
  name varchar(32) not null unique ,
  access_key varchar(255) not null primary key,
  secret_key varchar(255) not null
);


drop table if exists streams;
create table streams (
  arn varchar(255) primary key not null,
  access_key varchar(32) not null,
  status varchar(16) not null,
  state_change timestamp not null,
  expiry_time timestamp not null,
  feeder_pid int
);


