DROP VIEW IF EXISTS overview;
DROP VIEW IF EXISTS tmp_overview_loc_merged;
DROP VIEW IF EXISTS tmp_overview_box_loc;
DROP VIEW IF EXISTS tmp_overview_loc;
DROP VIEW IF EXISTS tmp_overview_box;
DROP VIEW IF EXISTS tmp_overview;


CREATE OR REPLACE VIEW public.tmp_overview as
	SELECT
		b.box AS object,
		'box' AS affiliation,
		b.type AS type
	FROM lab_boxes b
UNION
	SELECT
		r.reagent AS object,
		'reagent' AS affiliation,
		r.type AS type
   	FROM lab_reagents r;


CREATE OR REPLACE VIEW public.tmp_overview_loc as
	SELECT DISTINCT
		o.object,
		l.new_location AS location
	FROM
		tmp_overview o,
		lab_movementlog l
	WHERE
  		l."timestamp" = ((	SELECT
  								max(l."timestamp") AS max
       						FROM
       							lab_movementlog l
									where
										l.object::text = o.object::text));


CREATE OR REPLACE VIEW public.tmp_overview_box as
	SELECT
		o.object,
		b.box AS box,
		b.position AS position
	FROM
		tmp_overview o,
		lab_boxinglog b
	WHERE
  		b."timestamp" = ((	SELECT
  								max(b."timestamp") AS max
       						FROM
       							lab_boxinglog b
									where
										b.object::text = o.object::text));


CREATE OR REPLACE VIEW public.tmp_overview_box_loc AS
  SELECT
		b.object,
		l.location
  FROM
		tmp_overview_box b,
		tmp_overview_loc l
	WHERE
		l.object::text = b.box::text;


CREATE OR REPLACE VIEW public.tmp_overview_loc_merged AS
	SELECT
		l.object,
		l.location
	FROM
		tmp_overview_loc l
UNION
	SELECT
		b.object,
		b.location
	FROM tmp_overview_box_loc b;




CREATE OR REPLACE VIEW public.overview AS
	SELECT
		row_number() OVER () AS id,
    r.object,
		r.affiliation,
    r.type,
		tmp_overview_loc_merged.location,
		tmp_overview_box.box AS box,
		tmp_overview_box.position AS position
	FROM
		tmp_overview r
	LEFT JOIN
		tmp_overview_loc_merged ON r.object::text = tmp_overview_loc_merged.object::text
	LEFT JOIN
		tmp_overview_box ON r.object::text = tmp_overview_box.object::text;