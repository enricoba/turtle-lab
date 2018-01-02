drop view rtd;
drop view tmp_rtd_freeze;
drop view tmp_rtd_times;
drop view tmp_rtd_loc;
drop view tmp_rtd;

-- union samples and boxes to get all boxes and samples in one view
-- mark them as 'samples' or 'box' depending their table origin as type
CREATE OR REPLACE VIEW public.tmp_rtd as
	SELECT
		s.sample AS object,
		'sample' AS "type"
	FROM lab_samples s
UNION
	SELECT
		b.box AS object,
    	'box' AS "type"
   	FROM lab_boxes b;

-- create new view selecting object from tmp_rtd and get all actual locations for moved objects
-- this excludes non-moved pobjects
CREATE OR REPLACE VIEW public.tmp_rtd_loc AS
	SELECT
		r.object,
    	l.new_location AS location
   	FROM
   		tmp_rtd r,
    	lab_movementlog l
  	WHERE
  		l."timestamp" = ((	SELECT
  								max(l."timestamp") AS max
       						FROM
       							lab_movementlog l
          					where
          						l.object::text = r.object::text));

-- view to get max thaw counts from linked freeze thaw account
-- only includes samples because boxes dont have freeze thaw accounts
create or replace view public.tmp_rtd_count as
	select
		s.sample as object,
 		f.thaw_count - ((select
 							count(t.method)
 						from
 							lab_times t
 						where
 							t."item" = s."sample" and t.method::text = 'thaw')) as remaining_thaw_count
 	from
 		lab_samples s,
 		lab_freezethawaccounts f
 	where
		f."account" = s."account";


-- view for remaining freeze time
create or replace view public.tmp_rtd_duration as
	select
		s.sample as object,
		sum(t.duration) as duration
	from
		lab_samples s,
		lab_times t
	where
		s."sample" = t."item" and t.method::text = 'freeze'
	group by
		s.sample;


create or replace view public.tmp_rtd_freeze as
	select
		d.object,
		case
			when d.duration is null
			then f.freeze_time
			else f.freeze_time - d.duration
		end as remaining_freeze_time
	from
		tmp_rtd_duration d,
		lab_freezethawaccounts f
	where
		f."account" = ((SELECT
							account
       					FROM
   							lab_samples s
      					where
      						s."sample" = d.object::text));

-- final view
CREATE OR REPLACE VIEW public.rtd AS
	SELECT
		row_number() OVER () AS id,
    	r.object,
    	r.type,
    	tmp_rtd_loc.location,
    	tmp_rtd_count.remaining_thaw_count,
    	tmp_rtd_freeze.remaining_freeze_time
   	FROM
   		tmp_rtd r
 	LEFT JOIN
 		tmp_rtd_loc ON r.object::text = tmp_rtd_loc.object::text
 	left join
 		tmp_rtd_count on r.object::text = tmp_rtd_count.object::text
 	left join
 		tmp_rtd_freeze on r.object::text = tmp_rtd_freeze.object::text;