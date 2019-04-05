--针对Stack Overflow建表
create table stackoverflow_info(
    links int(11) not null primary key,
    views int(11),
    votes int(11),
    answers int(11),
    tags text,
    questions text,
    questionstate text,
    adoptedcode text,
    adopted text
);

--针对Github建表
create table github_info(
    author varchar(255),
    title text,
    star text,
    des text,
    tag text,
    update_date text,
    file_urls text
);
