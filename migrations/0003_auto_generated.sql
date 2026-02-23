-- upgrade

ALTER TABLE materias ADD COLUMN codigo VARCHAR(50) 

-- rollback

ALTER TABLE materias DROP COLUMN codigo
