create table budget
(
    id integer primary key,
    codename varchar(255),
    daily_limit integer,
    income integer,
    created datetime
);

create table category
(
    codename        varchar(255) primary key,
    name            varchar(255),
    is_base_expense boolean,
    aliases         text,
    int not null
);

create table expense(
    id integer primary key,
    amount integer,
    created datetime,
    category_codename integer,
    raw_text text,
    FOREIGN KEY(category_codename) REFERENCES category(codename)
);

insert into category (codename, name, category.is_base_expense, aliases)
select *
from (select *from (values ("products", "продукты", true, "еда, сильпо, космос, рынок, метро, metro"),
             ("coffee", "кофе", false, ""),
             ("animals", "животные", true, "корм, песок, пакеты, поводок, ошейник, игрухи"),
             ("cafe", "кафе", false, "ресторан, рест, мак, макдональдс, макдак, kfc, алхимия, вайнинсайд, wineinside"),
             ("car", "машина", true, "газ, бензин, масло, сто, колеса, мойка, бенз, топливо"),
             ("taxi", "такси", false, "бонд, болт, 838"),
             ("communications", "коммуникации", true, "инет, inet, beetec, битек"),
             ("chems", "химия", true, "бытовая, порошек, ополаскиватель, мыло"),
             ("generator", "генератор", true, "гена, генчик"),
             ("subscriptions", "подписки", true, "подписка, эпл, нетфликс, netflix, apple"),
             ("other", "прочее", false, "");

