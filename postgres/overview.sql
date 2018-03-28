drop view overview;
drop view tmp_overview;



CREATE OR REPLACE VIEW public.tmp_overview as
	SELECT
		s.sample AS object,
		'sample' AS "type"
	FROM lab_samples s
UNION
	SELECT
		r.reagent AS object,
    	'reagent' AS "type"
   	FROM lab_reagents r;


CREATE OR REPLACE VIEW public.overview AS
	SELECT
		row_number() OVER () AS id,
    r.object,
    r.type,
		'' AS location,
		'' AS box,
		'' AS position
	FROM
		tmp_overview r