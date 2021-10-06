-- upgrade --
ALTER TABLE "users" ADD "email_address" TEXT;
-- downgrade --
ALTER TABLE "users" DROP COLUMN "email_address";
