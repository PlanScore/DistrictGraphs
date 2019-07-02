--
-- Query series used to generate tables and columns for pgsql2graph.
-- Start with Census shapefiles for tracts, VTDs, block groups, and blocks.
--

-- states that touch the outside
alter table tl_2010_us_state10 add column is_border boolean default false;

update tl_2010_us_state10 as state
set is_border = ST_Relate(state.geom, country.geom, '****1****')
from tl_2010_us as country
;

select is_border, count(1) from tl_2010_us_state10 group by is_border;


-- counties that touch the outside
alter table tl_2010_us_county10 add column is_border boolean default false;

update tl_2010_us_county10 as county
set is_border = CASE
    WHEN state.is_border THEN ST_Relate(county.geom, country.geom, '****1****')
    ELSE false
    END
from tl_2010_us as country, tl_2010_us_state10 as state
WHERE state.statefp10 = county.statefp10
;

select is_border, count(1) from tl_2010_us_county10 group by is_border;


-- VTDs that touch the outside
alter table tl_2010_us_vtd10 add column is_border boolean;

update tl_2010_us_vtd10 as vtd
set is_border = CASE
    WHEN county.is_border THEN ST_Relate(vtd.geom, country.geom, '****1****')
    ELSE false
    END
from tl_2010_us as country, tl_2010_us_county10 as county
WHERE vtd.statefp10 = county.statefp10
  AND vtd.countyfp10 = county.countyfp10
;

select is_border, count(1) from tl_2010_us_vtd10 group by is_border;


-- tracts that touch the outside
alter table tl_2010_us_tract10 add column is_border boolean;

update tl_2010_us_tract10 as tract
set is_border = CASE
    WHEN county.is_border THEN ST_Relate(tract.geom, country.geom, '****1****')
    ELSE false
    END
from tl_2010_us as country, tl_2010_us_county10 as county
WHERE tract.statefp10 = county.statefp10
  AND tract.countyfp10 = county.countyfp10
;

select is_border, count(1) from tl_2010_us_tract10 group by is_border;


-- block groups that touch the outside
alter table tl_2010_us_bg10 add column is_border boolean;

update tl_2010_us_bg10 as bg
set is_border = CASE
    WHEN tract.is_border THEN ST_Relate(bg.geom, country.geom, '****1****')
    ELSE false
    END
from tl_2010_us as country, tl_2010_us_tract10 as tract
WHERE bg.statefp10 = tract.statefp10
  AND bg.countyfp10 = tract.countyfp10
  AND bg.tractce10 = tract.tractce10
;

select is_border, count(1) from tl_2010_us_bg10 group by is_border;


-- blocks that touch the outside
alter table tl_2010_us_tabblock10 add column is_border boolean;

update tl_2010_us_tabblock10 as block
set is_border = CASE
    WHEN tract.is_border THEN ST_Relate(block.geom, country.geom, '****1****')
    ELSE false
    END
from tl_2010_us as country, tl_2010_us_tract10 as tract
WHERE block.statefp10 = tract.statefp10
  AND block.countyfp10 = tract.countyfp10
  AND block.tractce10 = tract.tractce10
;

select is_border, count(1) from tl_2010_us_tabblock10 group by is_border;


-- cluster on GEOID10
alter table tl_2010_us_vtd10 alter column geoid10 set not null;
create index tl_2010_us_vtd10_geoid10 on tl_2010_us_vtd10 (geoid10);
cluster tl_2010_us_vtd10 using tl_2010_us_vtd10_geoid10;

alter table tl_2010_us_tract10 alter column geoid10 set not null;
create index tl_2010_us_tract10_geoid10 on tl_2010_us_tract10 (geoid10);
cluster tl_2010_us_tract10 using tl_2010_us_tract10_geoid10;

alter table tl_2010_us_bg10 alter column geoid10 set not null;
create index tl_2010_us_bg10_geoid10 on tl_2010_us_bg10 (geoid10);
cluster tl_2010_us_bg10 using tl_2010_us_bg10_geoid10;

alter table tl_2010_us_tabblock10 alter column geoid10 set not null;
create index tl_2010_us_tabblock10_geoid10 on tl_2010_us_tabblock10 (geoid10);
cluster tl_2010_us_tabblock10 using tl_2010_us_tabblock10_geoid10;



-- boundaries between pairs of tracts in Del Norte County, CA
drop table if exists edges_us_tract10;
create table edges_us_tract10
as
select tract1.geoid10 as geoid10a, tract2.geoid10 as geoid10b,
    tract1.statefp10 as statefp10a, tract1.countyfp10 as countyfp10a,
    (tract1.statefp10 = tract2.statefp10) as same_state,
    (tract1.statefp10 = tract2.statefp10 and tract1.countyfp10 = tract2.countyfp10) as same_county
from tl_2010_us_tract10 as tract1
join tl_2010_us_tract10 as tract2
    on tract1.geom && tract2.geom
    and tract1.gid != tract2.gid
    and ST_Relate(tract1.geom, tract2.geom, 'F***1****')
--where tract1.statefp10 = '06'
--  and tract1.countyfp10 = '015'
order by tract1.geoid10, tract2.geoid10
;

insert into edges_us_tract10
select geoid10, null, statefp10, countyfp10, false, false
from tl_2010_us_tract10
where is_border
;

-- boundaries between pairs of VTDs in Del Norte County, CA
drop table if exists edges_us_vtd10;
create table edges_us_vtd10
as
select vtd1.geoid10 as geoid10a, vtd2.geoid10 as geoid10b,
    vtd1.statefp10 as statefp10a, vtd1.countyfp10 as countyfp10a,
    (vtd1.statefp10 = vtd2.statefp10) as same_state,
    (vtd1.statefp10 = vtd2.statefp10 and vtd1.countyfp10 = vtd2.countyfp10) as same_county
from tl_2010_us_vtd10 as vtd1
join tl_2010_us_vtd10 as vtd2
    on vtd1.geom && vtd2.geom
    and vtd1.gid != vtd2.gid
    and ST_Relate(vtd1.geom, vtd2.geom, 'F***1****')
--where vtd1.statefp10 = '06'
--  and vtd1.countyfp10 = '015'
order by vtd1.geoid10, vtd2.geoid10
;

insert into edges_us_vtd10
select geoid10, null, statefp10, countyfp10, false, false
from tl_2010_us_vtd10
where is_border
;

-- boundaries between pairs of block groups in Del Norte County, CA
drop table if exists edges_us_bg10;
create table edges_us_bg10
as
select bg1.geoid10 as geoid10a, bg2.geoid10 as geoid10b,
    bg1.statefp10 as statefp10a, bg1.countyfp10 as countyfp10a,
    (bg1.statefp10 = bg2.statefp10) as same_state,
    (bg1.statefp10 = bg2.statefp10 and bg1.countyfp10 = bg2.countyfp10) as same_county
from tl_2010_us_bg10 as bg1
join tl_2010_us_bg10 as bg2
    on bg1.geom && bg2.geom
    and bg1.gid != bg2.gid
    and ST_Relate(bg1.geom, bg2.geom, 'F***1****')
--where bg1.statefp10 = '06'
--  and bg1.countyfp10 = '015'
order by bg1.geoid10, bg2.geoid10
;

insert into edges_us_bg10
select geoid10, null, statefp10, countyfp10, false, false
from tl_2010_us_bg10
where is_border
;

-- boundaries between pairs of blocks in Del Norte County, CA
drop table if exists edges_us_tabblock10;
create table edges_us_tabblock10
as
select block1.geoid10 as geoid10a, block2.geoid10 as geoid10b,
    block1.statefp10 as statefp10a, block1.countyfp10 as countyfp10a,
    (block1.statefp10 = block2.statefp10) as same_state,
    (block1.statefp10 = block2.statefp10 and block1.countyfp10 = block2.countyfp10) as same_county
from tl_2010_us_tabblock10 as block1
join tl_2010_us_tabblock10 as block2
    on block1.geom && block2.geom
    and block1.gid != block2.gid
    and ST_Relate(block1.geom, block2.geom, 'F***1****')
--where block1.statefp10 = '06'
--  and block1.countyfp10 = '015'
order by block1.geoid10, block2.geoid10
;

insert into edges_us_tabblock10
select geoid10, null, statefp10, countyfp10, false, false
from tl_2010_us_tabblock10
where is_border
;

--
alter table edges_us_tract10 alter column geoid10a set not null;
create index edges_us_tract10_geoid10a on edges_us_tract10 (geoid10a);
create index edges_us_tract10_county on edges_us_tract10 (statefp10a, countyfp10a);
cluster edges_us_tract10 using edges_us_tract10_geoid10a;

alter table edges_us_vtd10 alter column geoid10a set not null;
create index edges_us_vtd10_geoid10a on edges_us_vtd10 (geoid10a);
create index edges_us_vtd10_county on edges_us_vtd10 (statefp10a, countyfp10a);
cluster edges_us_vtd10 using edges_us_vtd10_geoid10a;

alter table edges_us_bg10 alter column geoid10a set not null;
create index edges_us_bg10_geoid10a on edges_us_bg10 (geoid10a);
create index edges_us_bg10_county on edges_us_bg10 (statefp10a, countyfp10a);
cluster edges_us_bg10 using edges_us_bg10_geoid10a;

alter table edges_us_tabblock10 alter column geoid10a set not null;
create index edges_us_tabblock10_geoid10a on edges_us_tabblock10 (geoid10a);
create index edges_us_tabblock10_county on edges_us_tabblock10 (statefp10a, countyfp10a);
cluster edges_us_tabblock10 using edges_us_tabblock10_geoid10a;
