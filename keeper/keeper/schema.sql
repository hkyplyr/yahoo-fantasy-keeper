drop table if exists current_pick;
create table current_pick (
    id integer PRIMARY KEY,
    pick integer
);

insert into current_pick (pick) values (1);

drop table if exists draft;
create table draft (
    pick integer PRIMARY KEY,
    player text not null
);

drop table if exists keeper;
create table keeper (
    id integer PRIMARY KEY,
    player text not null,
    pick integer not null
);

insert into keeper (player, pick) values ('TestPlayer', 13);
insert into keeper (player, pick) values ('TestPlayer', 26);
insert into keeper (player, pick) values ('TestPlayer', 39);
insert into keeper (player, pick) values ('TestPlayer', 52);
insert into keeper (player, pick) values ('TestPlayer', 65);
insert into keeper (player, pick) values ('TestPlayer', 78);
insert into keeper (player, pick) values ('TestPlayer', 91);
insert into keeper (player, pick) values ('TestPlayer', 104);
insert into keeper (player, pick) values ('TestPlayer', 117);
insert into keeper (player, pick) values ('TestPlayer', 130);
insert into keeper (player, pick) values ('TestPlayer', 143);
insert into keeper (player, pick) values ('TestPlayer', 156);
insert into keeper (player, pick) values ('TestPlayer', 169);
insert into keeper (player, pick) values ('TestPlayer', 182);
insert into keeper (player, pick) values ('TestPlayer', 195);
insert into keeper (player, pick) values ('TestPlayer', 208);
insert into keeper (player, pick) values ('TestPlayer', 221);

drop table if exists teams;
create table teams (
    id integer PRIMARY KEY,
    name text not null,
    url text not null,
    logo_url text not null,
    waiver integer not null,
    faab integer not null,
    moves integer not null,
    trades integer not null,
    mgr_name text not null,
    mgr_email text not null,
    mgr_logo text not null
);