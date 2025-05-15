CREATE TYPE "public"."case_version" AS ENUM('1.1');
CREATE TYPE "public"."class_type" AS ENUM('homeroom', 'scheduled');
CREATE TYPE "public"."client_app_status" AS ENUM('enabled', 'disabled');
CREATE TYPE "public"."difficulty" AS ENUM('easy', 'medium', 'hard');
CREATE TYPE "public"."enrollment_role" AS ENUM('administrator', 'proctor', 'student', 'teacher');
CREATE TYPE "public"."guid_type" AS ENUM('academicSession', 'assessmentLineItem', 'category', 'class', 'course', 'demographics', 'enrollment', 'gradingPeriod', 'lineItem', 'org', 'resource', 'result', 'scoreScale', 'student', 'teacher', 'term', 'user', 'componentResource', 'courseComponent');
CREATE TYPE "public"."gender" AS ENUM('male', 'female');
CREATE TYPE "public"."importance" AS ENUM('primary', 'secondary');
CREATE TYPE "public"."org_type" AS ENUM('department', 'school', 'district', 'local', 'state', 'national');
CREATE TYPE "public"."question_type" AS ENUM('choice', 'order', 'associate', 'match', 'hotspot', 'hottext', 'select-point', 'graphic-order', 'graphic-associate', 'graphic-gap-match', 'text-entry', 'extended-text', 'inline-choice', 'upload', 'slider', 'drawing', 'media', 'custom');
CREATE TYPE "public"."resource_sub_type" AS ENUM('qti-test', 'qti-question', 'qti-stimulus', 'qti-test-bank', 'unit', 'course', 'resource-collection');
CREATE TYPE "public"."resource_type" AS ENUM('qti', 'text', 'audio', 'video', 'interactive', 'visual', 'course-material');
CREATE TYPE "public"."role" AS ENUM('administrator', 'aide', 'guardian', 'parent', 'proctor', 'relative', 'student', 'teacher');
CREATE TYPE "public"."role_type" AS ENUM('primary', 'secondary');
CREATE TYPE "public"."score_status" AS ENUM('exempt', 'fully graded', 'not submitted', 'partially graded', 'submitted');
CREATE TYPE "public"."session_type" AS ENUM('gradingPeriod', 'semester', 'schoolYear', 'term');
CREATE TYPE "public"."status_type" AS ENUM('active', 'tobedeleted');
CREATE TABLE "cf_association" (
	"sourced_id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"association_type" text NOT NULL,
	"sequence_number" integer,
	"uri" text NOT NULL,
	"origin_node_id" uuid,
	"destination_node_id" uuid,
	"last_change_date_time" timestamp DEFAULT now() NOT NULL,
	"origin_document_id" uuid,
	"destination_document_id" uuid,
	"association_grouping_id" uuid
);

CREATE TABLE "cf_document" (
	"sourced_id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"uri" text NOT NULL,
	"framework_type" text,
	"case_version" "case_version" DEFAULT '1.1',
	"creator" text NOT NULL,
	"title" text NOT NULL,
	"last_change_date_time" timestamp DEFAULT now() NOT NULL,
	"official_source_url" text,
	"publisher" text,
	"description" text,
	"subject" jsonb DEFAULT '[]'::jsonb,
	"subject_uri" jsonb DEFAULT '[]'::jsonb,
	"language" text,
	"version" text,
	"adoption_status" text,
	"status_start_date" timestamp,
	"status_end_date" timestamp,
	"license_uri" jsonb,
	"notes" text,
	"extensions" jsonb
);

CREATE TABLE "cf_item" (
	"sourced_id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"full_statement" text NOT NULL,
	"alternative_label" text,
	"cf_item_type" text NOT NULL,
	"uri" text NOT NULL,
	"human_coding_scheme" text,
	"list_enumeration" text,
	"abbreviated_statement" text,
	"concept_keywords" jsonb DEFAULT '[]'::jsonb,
	"concept_keywords_uri" jsonb,
	"notes" text,
	"subject" jsonb DEFAULT '[]'::jsonb,
	"subject_uri" jsonb DEFAULT '[]'::jsonb,
	"language" text,
	"education_level" jsonb DEFAULT '[]'::jsonb,
	"cf_item_type_uri" jsonb,
	"license_uri" jsonb,
	"status_start_date" timestamp,
	"status_end_date" timestamp,
	"last_change_date_time" timestamp DEFAULT now() NOT NULL,
	"extensions" jsonb,
	"cf_document_uri_title" text NOT NULL,
	"cf_document_uri_identifier" text NOT NULL,
	"cf_document_uri_uri" text NOT NULL,
	"document_id" uuid NOT NULL
);

CREATE TABLE "academic_sessions" (
	"tenant_id" uuid,
	"client_app_id" uuid,
	"sourced_id" text PRIMARY KEY NOT NULL,
	"status" "status_type" DEFAULT 'active' NOT NULL,
	"date_last_modified" timestamp DEFAULT now() NOT NULL,
	"metadata" jsonb DEFAULT 'null'::jsonb,
	"title" text NOT NULL,
	"start_date" timestamp NOT NULL,
	"end_date" timestamp NOT NULL,
	"type" "session_type" NOT NULL,
	"parent_sourced_id" text,
	"school_year" text NOT NULL,
	"org_sourced_id" text NOT NULL,
	"class_sourced_id" text
);

CREATE TABLE "assessment_line_items" (
	"tenant_id" uuid,
	"client_app_id" uuid,
	"sourced_id" text PRIMARY KEY NOT NULL,
	"status" "status_type" DEFAULT 'active' NOT NULL,
	"date_last_modified" timestamp DEFAULT now() NOT NULL,
	"metadata" jsonb DEFAULT 'null'::jsonb,
	"title" text NOT NULL,
	"description" text,
	"class_sourced_id" text,
	"parent_sourced_id" text,
	"score_scale_sourced_id" text,
	"result_value_min" real,
	"result_value_max" real,
	"learning_objective_set" jsonb[],
	"component_resource_sourced_id" text,
	"component_sourced_id" text
);

CREATE TABLE "assessment_results" (
	"tenant_id" uuid,
	"client_app_id" uuid,
	"sourced_id" text PRIMARY KEY NOT NULL,
	"status" "status_type" DEFAULT 'active' NOT NULL,
	"date_last_modified" timestamp DEFAULT now() NOT NULL,
	"metadata" jsonb DEFAULT 'null'::jsonb,
	"assessment_line_item_sourced_id" text NOT NULL,
	"student_sourced_id" text NOT NULL,
	"score" real,
	"text_score" text,
	"score_date" timestamp NOT NULL,
	"score_scale_sourced_id" text,
	"score_percentile" real,
	"score_status" "score_status" NOT NULL,
	"comment" text,
	"learning_objective_set" jsonb,
	"in_progress" boolean,
	"incomplete" boolean,
	"late" boolean,
	"missing" boolean
);

CREATE TABLE "categories" (
	"tenant_id" uuid,
	"client_app_id" uuid,
	"sourced_id" text PRIMARY KEY NOT NULL,
	"status" "status_type" DEFAULT 'active' NOT NULL,
	"date_last_modified" timestamp DEFAULT now() NOT NULL,
	"metadata" jsonb DEFAULT 'null'::jsonb,
	"title" text NOT NULL,
	"weight" real
);

CREATE TABLE "class_academic_sessions" (
	"id" text PRIMARY KEY NOT NULL,
	"class_sourced_id" text NOT NULL,
	"academic_session_sourced_id" text NOT NULL,
	"date_last_modified" timestamp DEFAULT now() NOT NULL
);

CREATE TABLE "class_resources" (
	"tenant_id" uuid,
	"client_app_id" uuid,
	"id" text PRIMARY KEY NOT NULL,
	"class_sourced_id" text NOT NULL,
	"resource_sourced_id" text NOT NULL,
	"date_assigned" timestamp DEFAULT now() NOT NULL
);

CREATE TABLE "classes" (
	"tenant_id" uuid,
	"client_app_id" uuid,
	"sourced_id" text PRIMARY KEY NOT NULL,
	"status" "status_type" DEFAULT 'active' NOT NULL,
	"date_last_modified" timestamp DEFAULT now() NOT NULL,
	"metadata" jsonb DEFAULT 'null'::jsonb,
	"title" text NOT NULL,
	"class_code" text,
	"class_type" "class_type" NOT NULL,
	"location" text,
	"grades" text[],
	"subjects" text[],
	"subject_codes" text[],
	"periods" text[],
	"course_sourced_id" text NOT NULL,
	"school_sourced_id" text NOT NULL
);

CREATE TABLE "component_resources" (
	"tenant_id" uuid,
	"client_app_id" uuid,
	"sourced_id" text PRIMARY KEY NOT NULL,
	"status" "status_type" DEFAULT 'active' NOT NULL,
	"date_last_modified" timestamp DEFAULT now() NOT NULL,
	"metadata" jsonb DEFAULT 'null'::jsonb,
	"title" text NOT NULL,
	"component_sourced_id" text,
	"resource_sourced_id" text,
	"sort_order" integer DEFAULT 0
);

CREATE TABLE "course_components" (
	"tenant_id" uuid,
	"client_app_id" uuid,
	"sourced_id" text PRIMARY KEY NOT NULL,
	"status" "status_type" DEFAULT 'active' NOT NULL,
	"date_last_modified" timestamp DEFAULT now() NOT NULL,
	"metadata" jsonb DEFAULT 'null'::jsonb,
	"course_sourced_id" text NOT NULL,
	"parent_sourced_id" text,
	"title" text NOT NULL,
	"sort_order" integer DEFAULT 0,
	"prerequisites" text[],
	"prerequisite_criteria" text,
	"unlock_date" timestamp
);

CREATE TABLE "course_resources" (
	"tenant_id" uuid,
	"client_app_id" uuid,
	"id" text PRIMARY KEY NOT NULL,
	"course_sourced_id" text NOT NULL,
	"resource_sourced_id" text NOT NULL,
	"date_assigned" timestamp DEFAULT now() NOT NULL
);

CREATE TABLE "courses" (
	"tenant_id" uuid,
	"client_app_id" uuid,
	"sourced_id" text PRIMARY KEY NOT NULL,
	"status" "status_type" DEFAULT 'active' NOT NULL,
	"date_last_modified" timestamp DEFAULT now() NOT NULL,
	"metadata" jsonb DEFAULT 'null'::jsonb,
	"title" text NOT NULL,
	"school_year_sourced_id" text,
	"course_code" text,
	"grades" text[],
	"org_sourced_id" text NOT NULL,
	"subjects" text[],
	"subject_codes" text[],
	"level" text,
	"grading_scheme" text
);

CREATE TABLE "demographics" (
	"tenant_id" uuid,
	"client_app_id" uuid,
	"sourced_id" text PRIMARY KEY NOT NULL,
	"status" "status_type" DEFAULT 'active' NOT NULL,
	"date_last_modified" timestamp DEFAULT now() NOT NULL,
	"metadata" jsonb DEFAULT 'null'::jsonb,
	"birth_date" timestamp,
	"sex" "gender",
	"american_indian_or_alaska_native" boolean DEFAULT false,
	"asian" boolean DEFAULT false,
	"black_or_african_american" boolean DEFAULT false,
	"native_hawaiian_or_other_pacific_islander" boolean DEFAULT false,
	"white" boolean DEFAULT false,
	"demographic_race_two_or_more_races" boolean DEFAULT false,
	"hispanic_or_latino_ethnicity" boolean DEFAULT false,
	"country_of_birth_code" text,
	"state_of_birth_abbreviation" text,
	"city_of_birth" text,
	"public_school_residence_status" text
);

CREATE TABLE "enrollments" (
	"tenant_id" uuid,
	"client_app_id" uuid,
	"sourced_id" text PRIMARY KEY NOT NULL,
	"status" "status_type" DEFAULT 'active' NOT NULL,
	"date_last_modified" timestamp DEFAULT now() NOT NULL,
	"metadata" jsonb DEFAULT 'null'::jsonb,
	"user_sourced_id" text NOT NULL,
	"class_sourced_id" text NOT NULL,
	"role" "enrollment_role" NOT NULL,
	"primary" boolean DEFAULT false NOT NULL,
	"begin_date" timestamp,
	"end_date" timestamp
);

CREATE TABLE "learning_objectives" (
	"tenant_id" uuid,
	"client_app_id" uuid,
	"id" serial PRIMARY KEY NOT NULL,
	"source" text NOT NULL,
	"learning_objective_id" text NOT NULL,
	"resource_metadata_sourced_id" text NOT NULL
);

CREATE TABLE "line_items" (
	"tenant_id" uuid,
	"client_app_id" uuid,
	"sourced_id" text PRIMARY KEY NOT NULL,
	"status" "status_type" DEFAULT 'active' NOT NULL,
	"date_last_modified" timestamp DEFAULT now() NOT NULL,
	"metadata" jsonb DEFAULT 'null'::jsonb,
	"title" text NOT NULL,
	"assign_date" timestamp NOT NULL,
	"due_date" timestamp NOT NULL,
	"class_sourced_id" text NOT NULL,
	"school_sourced_id" text NOT NULL,
	"category_sourced_id" text NOT NULL,
	"description" text,
	"grading_period_sourced_id" text,
	"academic_session_sourced_id" text,
	"score_scale_sourced_id" text,
	"result_value_min" real,
	"result_value_max" real,
	"learning_objective_set" jsonb[]
);

CREATE TABLE "orgs" (
	"tenant_id" uuid,
	"client_app_id" uuid,
	"sourced_id" text PRIMARY KEY NOT NULL,
	"status" "status_type" DEFAULT 'active' NOT NULL,
	"date_last_modified" timestamp DEFAULT now() NOT NULL,
	"metadata" jsonb DEFAULT 'null'::jsonb,
	"name" text NOT NULL,
	"type" "org_type" NOT NULL,
	"identifier" text,
	"parent_sourced_id" text
);

CREATE TABLE "resources" (
	"tenant_id" uuid,
	"client_app_id" uuid,
	"sourced_id" text PRIMARY KEY NOT NULL,
	"status" "status_type" DEFAULT 'active' NOT NULL,
	"date_last_modified" timestamp DEFAULT now() NOT NULL,
	"metadata" jsonb DEFAULT 'null'::jsonb,
	"title" text NOT NULL,
	"roles" "role_type"[],
	"importance" "importance" NOT NULL,
	"vendor_resource_id" text NOT NULL,
	"vendor_id" text,
	"application_id" text
);

CREATE TABLE "resources_metadata" (
	"tenant_id" uuid,
	"client_app_id" uuid,
	"sourced_id" text PRIMARY KEY NOT NULL,
	"type" "resource_type" NOT NULL,
	"sub_type" "resource_sub_type",
	"subject" text,
	"grades" integer[],
	"language" text,
	"xp" integer,
	"url" text,
	"keywords" text[],
	"lesson_type" text,
	"question_type" "question_type",
	"difficulty" "difficulty",
	"format" text,
	"author" text,
	"page_count" integer,
	"duration" text,
	"speaker" text,
	"captions_available" boolean,
	"launch_url" text,
	"tool_provider" text,
	"instructional_method" text,
	"resolution" text
);

CREATE TABLE "results" (
	"tenant_id" uuid,
	"client_app_id" uuid,
	"sourced_id" text PRIMARY KEY NOT NULL,
	"status" "status_type" DEFAULT 'active' NOT NULL,
	"date_last_modified" timestamp DEFAULT now() NOT NULL,
	"metadata" jsonb DEFAULT 'null'::jsonb,
	"line_item_sourced_id" text NOT NULL,
	"student_sourced_id" text NOT NULL,
	"class_sourced_id" text,
	"score_scale_sourced_id" text,
	"score_status" "score_status" NOT NULL,
	"score" real,
	"text_score" text,
	"score_date" timestamp NOT NULL,
	"comment" text,
	"learning_objective_set" jsonb[],
	"in_progress" boolean DEFAULT false NOT NULL,
	"incomplete" boolean DEFAULT false NOT NULL,
	"late" boolean DEFAULT false NOT NULL,
	"missing" boolean DEFAULT false NOT NULL
);

CREATE TABLE "score_scales" (
	"tenant_id" uuid,
	"client_app_id" uuid,
	"sourced_id" text PRIMARY KEY NOT NULL,
	"status" "status_type" DEFAULT 'active' NOT NULL,
	"date_last_modified" timestamp DEFAULT now() NOT NULL,
	"metadata" jsonb DEFAULT 'null'::jsonb,
	"title" text NOT NULL,
	"type" text NOT NULL,
	"course_sourced_id" text,
	"class_sourced_id" text NOT NULL,
	"score_scale_value" jsonb NOT NULL
);

CREATE TABLE "user_agents" (
	"id" text PRIMARY KEY NOT NULL,
	"user_sourced_id" text NOT NULL,
	"agent_sourced_id" text NOT NULL
);

CREATE TABLE "user_ids" (
	"tenant_id" uuid,
	"client_app_id" uuid,
	"sourced_id" text PRIMARY KEY NOT NULL,
	"status" "status_type" DEFAULT 'active' NOT NULL,
	"date_last_modified" timestamp DEFAULT now() NOT NULL,
	"metadata" jsonb DEFAULT 'null'::jsonb,
	"type" text NOT NULL,
	"identifier" text NOT NULL,
	"user_sourced_id" text NOT NULL
);

CREATE TABLE "user_profiles" (
	"sourced_id" text PRIMARY KEY NOT NULL,
	"status" "status_type" DEFAULT 'active' NOT NULL,
	"date_last_modified" timestamp DEFAULT now() NOT NULL,
	"metadata" jsonb DEFAULT 'null'::jsonb,
	"profile_id" text NOT NULL,
	"profile_type" text NOT NULL,
	"vendor_id" text NOT NULL,
	"application_id" text,
	"description" text,
	"user_sourced_id" text NOT NULL
);

CREATE TABLE "user_resources" (
	"tenant_id" uuid,
	"client_app_id" uuid,
	"id" text PRIMARY KEY NOT NULL,
	"user_sourced_id" text NOT NULL,
	"resource_sourced_id" text NOT NULL,
	"date_assigned" timestamp DEFAULT now() NOT NULL
);

CREATE TABLE "user_roles" (
	"status" "status_type" DEFAULT 'active' NOT NULL,
	"date_last_modified" timestamp DEFAULT now() NOT NULL,
	"metadata" jsonb DEFAULT 'null'::jsonb,
	"role_type" "role_type" NOT NULL,
	"role" "role" NOT NULL,
	"user_sourced_id" text NOT NULL,
	"org_sourced_id" text NOT NULL,
	"begin_date" timestamp,
	"end_date" timestamp
);

CREATE TABLE "users" (
	"tenant_id" uuid,
	"client_app_id" uuid,
	"sourced_id" text PRIMARY KEY NOT NULL,
	"status" "status_type" DEFAULT 'active' NOT NULL,
	"date_last_modified" timestamp DEFAULT now() NOT NULL,
	"metadata" jsonb DEFAULT 'null'::jsonb,
	"username" text,
	"enabled_user" boolean DEFAULT true NOT NULL,
	"given_name" text NOT NULL,
	"family_name" text NOT NULL,
	"middle_name" text,
	"identifier" text,
	"email" text,
	"sms" text,
	"phone" text,
	"password" text,
	"grades" text[],
	"user_ids" jsonb[],
	"user_master_identifier" text,
	"preferred_first_name" text,
	"preferred_middle_name" text,
	"preferred_last_name" text,
	"pronouns" text,
	"primary_org" text
);

CREATE TABLE "client_apps" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"name" text,
	"client_id" text NOT NULL,
	"status" "client_app_status" DEFAULT 'enabled' NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	CONSTRAINT "client_apps_client_id_unique" UNIQUE("client_id")
);

CREATE TABLE "tenant_client_apps" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" uuid,
	"client_app_id" uuid,
	CONSTRAINT "tenant_client_apps_client_app_id_unique" UNIQUE("client_app_id")
);

CREATE TABLE "tenants" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"name" text NOT NULL
);

ALTER TABLE "cf_association" ADD CONSTRAINT "cf_association_origin_node_id_cf_item_sourced_id_fk" FOREIGN KEY ("origin_node_id") REFERENCES "public"."cf_item"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "cf_association" ADD CONSTRAINT "cf_association_destination_node_id_cf_item_sourced_id_fk" FOREIGN KEY ("destination_node_id") REFERENCES "public"."cf_item"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "cf_association" ADD CONSTRAINT "cf_association_origin_document_id_cf_document_sourced_id_fk" FOREIGN KEY ("origin_document_id") REFERENCES "public"."cf_document"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "cf_association" ADD CONSTRAINT "cf_association_destination_document_id_cf_document_sourced_id_fk" FOREIGN KEY ("destination_document_id") REFERENCES "public"."cf_document"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "cf_item" ADD CONSTRAINT "cf_item_document_id_cf_document_sourced_id_fk" FOREIGN KEY ("document_id") REFERENCES "public"."cf_document"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "academic_sessions" ADD CONSTRAINT "academic_sessions_tenant_id_tenants_id_fk" FOREIGN KEY ("tenant_id") REFERENCES "public"."tenants"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "academic_sessions" ADD CONSTRAINT "academic_sessions_client_app_id_client_apps_id_fk" FOREIGN KEY ("client_app_id") REFERENCES "public"."client_apps"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "academic_sessions" ADD CONSTRAINT "academic_sessions_parent_sourced_id_academic_sessions_sourced_id_fk" FOREIGN KEY ("parent_sourced_id") REFERENCES "public"."academic_sessions"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "academic_sessions" ADD CONSTRAINT "academic_sessions_org_sourced_id_orgs_sourced_id_fk" FOREIGN KEY ("org_sourced_id") REFERENCES "public"."orgs"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "academic_sessions" ADD CONSTRAINT "academic_sessions_class_sourced_id_classes_sourced_id_fk" FOREIGN KEY ("class_sourced_id") REFERENCES "public"."classes"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "assessment_line_items" ADD CONSTRAINT "assessment_line_items_tenant_id_tenants_id_fk" FOREIGN KEY ("tenant_id") REFERENCES "public"."tenants"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "assessment_line_items" ADD CONSTRAINT "assessment_line_items_client_app_id_client_apps_id_fk" FOREIGN KEY ("client_app_id") REFERENCES "public"."client_apps"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "assessment_line_items" ADD CONSTRAINT "assessment_line_items_class_sourced_id_classes_sourced_id_fk" FOREIGN KEY ("class_sourced_id") REFERENCES "public"."classes"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "assessment_line_items" ADD CONSTRAINT "assessment_line_items_parent_sourced_id_assessment_line_items_sourced_id_fk" FOREIGN KEY ("parent_sourced_id") REFERENCES "public"."assessment_line_items"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "assessment_line_items" ADD CONSTRAINT "assessment_line_items_score_scale_sourced_id_score_scales_sourced_id_fk" FOREIGN KEY ("score_scale_sourced_id") REFERENCES "public"."score_scales"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "assessment_line_items" ADD CONSTRAINT "assessment_line_items_component_resource_sourced_id_component_resources_sourced_id_fk" FOREIGN KEY ("component_resource_sourced_id") REFERENCES "public"."component_resources"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "assessment_line_items" ADD CONSTRAINT "assessment_line_items_component_sourced_id_course_components_sourced_id_fk" FOREIGN KEY ("component_sourced_id") REFERENCES "public"."course_components"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "assessment_results" ADD CONSTRAINT "assessment_results_tenant_id_tenants_id_fk" FOREIGN KEY ("tenant_id") REFERENCES "public"."tenants"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "assessment_results" ADD CONSTRAINT "assessment_results_client_app_id_client_apps_id_fk" FOREIGN KEY ("client_app_id") REFERENCES "public"."client_apps"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "assessment_results" ADD CONSTRAINT "assessment_results_assessment_line_item_sourced_id_assessment_line_items_sourced_id_fk" FOREIGN KEY ("assessment_line_item_sourced_id") REFERENCES "public"."assessment_line_items"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "assessment_results" ADD CONSTRAINT "assessment_results_student_sourced_id_users_sourced_id_fk" FOREIGN KEY ("student_sourced_id") REFERENCES "public"."users"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "assessment_results" ADD CONSTRAINT "assessment_results_score_scale_sourced_id_score_scales_sourced_id_fk" FOREIGN KEY ("score_scale_sourced_id") REFERENCES "public"."score_scales"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "categories" ADD CONSTRAINT "categories_tenant_id_tenants_id_fk" FOREIGN KEY ("tenant_id") REFERENCES "public"."tenants"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "categories" ADD CONSTRAINT "categories_client_app_id_client_apps_id_fk" FOREIGN KEY ("client_app_id") REFERENCES "public"."client_apps"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "class_academic_sessions" ADD CONSTRAINT "class_academic_sessions_class_sourced_id_classes_sourced_id_fk" FOREIGN KEY ("class_sourced_id") REFERENCES "public"."classes"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "class_academic_sessions" ADD CONSTRAINT "class_academic_sessions_academic_session_sourced_id_academic_sessions_sourced_id_fk" FOREIGN KEY ("academic_session_sourced_id") REFERENCES "public"."academic_sessions"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "class_resources" ADD CONSTRAINT "class_resources_tenant_id_tenants_id_fk" FOREIGN KEY ("tenant_id") REFERENCES "public"."tenants"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "class_resources" ADD CONSTRAINT "class_resources_client_app_id_client_apps_id_fk" FOREIGN KEY ("client_app_id") REFERENCES "public"."client_apps"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "class_resources" ADD CONSTRAINT "class_resources_class_sourced_id_classes_sourced_id_fk" FOREIGN KEY ("class_sourced_id") REFERENCES "public"."classes"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "class_resources" ADD CONSTRAINT "class_resources_resource_sourced_id_resources_sourced_id_fk" FOREIGN KEY ("resource_sourced_id") REFERENCES "public"."resources"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "classes" ADD CONSTRAINT "classes_tenant_id_tenants_id_fk" FOREIGN KEY ("tenant_id") REFERENCES "public"."tenants"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "classes" ADD CONSTRAINT "classes_client_app_id_client_apps_id_fk" FOREIGN KEY ("client_app_id") REFERENCES "public"."client_apps"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "classes" ADD CONSTRAINT "classes_course_sourced_id_courses_sourced_id_fk" FOREIGN KEY ("course_sourced_id") REFERENCES "public"."courses"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "classes" ADD CONSTRAINT "classes_school_sourced_id_orgs_sourced_id_fk" FOREIGN KEY ("school_sourced_id") REFERENCES "public"."orgs"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "component_resources" ADD CONSTRAINT "component_resources_tenant_id_tenants_id_fk" FOREIGN KEY ("tenant_id") REFERENCES "public"."tenants"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "component_resources" ADD CONSTRAINT "component_resources_client_app_id_client_apps_id_fk" FOREIGN KEY ("client_app_id") REFERENCES "public"."client_apps"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "component_resources" ADD CONSTRAINT "component_resources_component_sourced_id_course_components_sourced_id_fk" FOREIGN KEY ("component_sourced_id") REFERENCES "public"."course_components"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "component_resources" ADD CONSTRAINT "component_resources_resource_sourced_id_resources_sourced_id_fk" FOREIGN KEY ("resource_sourced_id") REFERENCES "public"."resources"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "course_components" ADD CONSTRAINT "course_components_tenant_id_tenants_id_fk" FOREIGN KEY ("tenant_id") REFERENCES "public"."tenants"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "course_components" ADD CONSTRAINT "course_components_client_app_id_client_apps_id_fk" FOREIGN KEY ("client_app_id") REFERENCES "public"."client_apps"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "course_components" ADD CONSTRAINT "course_components_course_sourced_id_courses_sourced_id_fk" FOREIGN KEY ("course_sourced_id") REFERENCES "public"."courses"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "course_components" ADD CONSTRAINT "course_components_parent_sourced_id_course_components_sourced_id_fk" FOREIGN KEY ("parent_sourced_id") REFERENCES "public"."course_components"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "course_resources" ADD CONSTRAINT "course_resources_tenant_id_tenants_id_fk" FOREIGN KEY ("tenant_id") REFERENCES "public"."tenants"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "course_resources" ADD CONSTRAINT "course_resources_client_app_id_client_apps_id_fk" FOREIGN KEY ("client_app_id") REFERENCES "public"."client_apps"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "course_resources" ADD CONSTRAINT "course_resources_course_sourced_id_courses_sourced_id_fk" FOREIGN KEY ("course_sourced_id") REFERENCES "public"."courses"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "course_resources" ADD CONSTRAINT "course_resources_resource_sourced_id_resources_sourced_id_fk" FOREIGN KEY ("resource_sourced_id") REFERENCES "public"."resources"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "courses" ADD CONSTRAINT "courses_tenant_id_tenants_id_fk" FOREIGN KEY ("tenant_id") REFERENCES "public"."tenants"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "courses" ADD CONSTRAINT "courses_client_app_id_client_apps_id_fk" FOREIGN KEY ("client_app_id") REFERENCES "public"."client_apps"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "courses" ADD CONSTRAINT "courses_school_year_sourced_id_academic_sessions_sourced_id_fk" FOREIGN KEY ("school_year_sourced_id") REFERENCES "public"."academic_sessions"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "courses" ADD CONSTRAINT "courses_org_sourced_id_orgs_sourced_id_fk" FOREIGN KEY ("org_sourced_id") REFERENCES "public"."orgs"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "demographics" ADD CONSTRAINT "demographics_tenant_id_tenants_id_fk" FOREIGN KEY ("tenant_id") REFERENCES "public"."tenants"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "demographics" ADD CONSTRAINT "demographics_client_app_id_client_apps_id_fk" FOREIGN KEY ("client_app_id") REFERENCES "public"."client_apps"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "demographics" ADD CONSTRAINT "demographics_sourced_id_users_sourced_id_fk" FOREIGN KEY ("sourced_id") REFERENCES "public"."users"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "enrollments" ADD CONSTRAINT "enrollments_tenant_id_tenants_id_fk" FOREIGN KEY ("tenant_id") REFERENCES "public"."tenants"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "enrollments" ADD CONSTRAINT "enrollments_client_app_id_client_apps_id_fk" FOREIGN KEY ("client_app_id") REFERENCES "public"."client_apps"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "enrollments" ADD CONSTRAINT "enrollments_user_sourced_id_users_sourced_id_fk" FOREIGN KEY ("user_sourced_id") REFERENCES "public"."users"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "enrollments" ADD CONSTRAINT "enrollments_class_sourced_id_classes_sourced_id_fk" FOREIGN KEY ("class_sourced_id") REFERENCES "public"."classes"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "learning_objectives" ADD CONSTRAINT "learning_objectives_tenant_id_tenants_id_fk" FOREIGN KEY ("tenant_id") REFERENCES "public"."tenants"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "learning_objectives" ADD CONSTRAINT "learning_objectives_client_app_id_client_apps_id_fk" FOREIGN KEY ("client_app_id") REFERENCES "public"."client_apps"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "learning_objectives" ADD CONSTRAINT "learning_objectives_resource_metadata_sourced_id_resources_metadata_sourced_id_fk" FOREIGN KEY ("resource_metadata_sourced_id") REFERENCES "public"."resources_metadata"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "line_items" ADD CONSTRAINT "line_items_tenant_id_tenants_id_fk" FOREIGN KEY ("tenant_id") REFERENCES "public"."tenants"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "line_items" ADD CONSTRAINT "line_items_client_app_id_client_apps_id_fk" FOREIGN KEY ("client_app_id") REFERENCES "public"."client_apps"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "line_items" ADD CONSTRAINT "line_items_class_sourced_id_classes_sourced_id_fk" FOREIGN KEY ("class_sourced_id") REFERENCES "public"."classes"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "line_items" ADD CONSTRAINT "line_items_school_sourced_id_orgs_sourced_id_fk" FOREIGN KEY ("school_sourced_id") REFERENCES "public"."orgs"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "line_items" ADD CONSTRAINT "line_items_category_sourced_id_categories_sourced_id_fk" FOREIGN KEY ("category_sourced_id") REFERENCES "public"."categories"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "line_items" ADD CONSTRAINT "line_items_grading_period_sourced_id_academic_sessions_sourced_id_fk" FOREIGN KEY ("grading_period_sourced_id") REFERENCES "public"."academic_sessions"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "line_items" ADD CONSTRAINT "line_items_academic_session_sourced_id_academic_sessions_sourced_id_fk" FOREIGN KEY ("academic_session_sourced_id") REFERENCES "public"."academic_sessions"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "line_items" ADD CONSTRAINT "line_items_score_scale_sourced_id_score_scales_sourced_id_fk" FOREIGN KEY ("score_scale_sourced_id") REFERENCES "public"."score_scales"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "orgs" ADD CONSTRAINT "orgs_tenant_id_tenants_id_fk" FOREIGN KEY ("tenant_id") REFERENCES "public"."tenants"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "orgs" ADD CONSTRAINT "orgs_client_app_id_client_apps_id_fk" FOREIGN KEY ("client_app_id") REFERENCES "public"."client_apps"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "orgs" ADD CONSTRAINT "orgs_parent_sourced_id_orgs_sourced_id_fk" FOREIGN KEY ("parent_sourced_id") REFERENCES "public"."orgs"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "resources" ADD CONSTRAINT "resources_tenant_id_tenants_id_fk" FOREIGN KEY ("tenant_id") REFERENCES "public"."tenants"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "resources" ADD CONSTRAINT "resources_client_app_id_client_apps_id_fk" FOREIGN KEY ("client_app_id") REFERENCES "public"."client_apps"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "resources_metadata" ADD CONSTRAINT "resources_metadata_tenant_id_tenants_id_fk" FOREIGN KEY ("tenant_id") REFERENCES "public"."tenants"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "resources_metadata" ADD CONSTRAINT "resources_metadata_client_app_id_client_apps_id_fk" FOREIGN KEY ("client_app_id") REFERENCES "public"."client_apps"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "resources_metadata" ADD CONSTRAINT "resources_metadata_sourced_id_resources_sourced_id_fk" FOREIGN KEY ("sourced_id") REFERENCES "public"."resources"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "results" ADD CONSTRAINT "results_tenant_id_tenants_id_fk" FOREIGN KEY ("tenant_id") REFERENCES "public"."tenants"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "results" ADD CONSTRAINT "results_client_app_id_client_apps_id_fk" FOREIGN KEY ("client_app_id") REFERENCES "public"."client_apps"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "results" ADD CONSTRAINT "results_line_item_sourced_id_line_items_sourced_id_fk" FOREIGN KEY ("line_item_sourced_id") REFERENCES "public"."line_items"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "results" ADD CONSTRAINT "results_student_sourced_id_users_sourced_id_fk" FOREIGN KEY ("student_sourced_id") REFERENCES "public"."users"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "results" ADD CONSTRAINT "results_class_sourced_id_classes_sourced_id_fk" FOREIGN KEY ("class_sourced_id") REFERENCES "public"."classes"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "results" ADD CONSTRAINT "results_score_scale_sourced_id_resources_sourced_id_fk" FOREIGN KEY ("score_scale_sourced_id") REFERENCES "public"."resources"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "score_scales" ADD CONSTRAINT "score_scales_tenant_id_tenants_id_fk" FOREIGN KEY ("tenant_id") REFERENCES "public"."tenants"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "score_scales" ADD CONSTRAINT "score_scales_client_app_id_client_apps_id_fk" FOREIGN KEY ("client_app_id") REFERENCES "public"."client_apps"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "score_scales" ADD CONSTRAINT "score_scales_course_sourced_id_courses_sourced_id_fk" FOREIGN KEY ("course_sourced_id") REFERENCES "public"."courses"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "score_scales" ADD CONSTRAINT "score_scales_class_sourced_id_classes_sourced_id_fk" FOREIGN KEY ("class_sourced_id") REFERENCES "public"."classes"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "user_agents" ADD CONSTRAINT "user_agents_user_sourced_id_users_sourced_id_fk" FOREIGN KEY ("user_sourced_id") REFERENCES "public"."users"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "user_agents" ADD CONSTRAINT "user_agents_agent_sourced_id_users_sourced_id_fk" FOREIGN KEY ("agent_sourced_id") REFERENCES "public"."users"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "user_ids" ADD CONSTRAINT "user_ids_tenant_id_tenants_id_fk" FOREIGN KEY ("tenant_id") REFERENCES "public"."tenants"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "user_ids" ADD CONSTRAINT "user_ids_client_app_id_client_apps_id_fk" FOREIGN KEY ("client_app_id") REFERENCES "public"."client_apps"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "user_ids" ADD CONSTRAINT "user_ids_user_sourced_id_users_sourced_id_fk" FOREIGN KEY ("user_sourced_id") REFERENCES "public"."users"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "user_profiles" ADD CONSTRAINT "user_profiles_user_sourced_id_users_sourced_id_fk" FOREIGN KEY ("user_sourced_id") REFERENCES "public"."users"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "user_resources" ADD CONSTRAINT "user_resources_tenant_id_tenants_id_fk" FOREIGN KEY ("tenant_id") REFERENCES "public"."tenants"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "user_resources" ADD CONSTRAINT "user_resources_client_app_id_client_apps_id_fk" FOREIGN KEY ("client_app_id") REFERENCES "public"."client_apps"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "user_resources" ADD CONSTRAINT "user_resources_user_sourced_id_users_sourced_id_fk" FOREIGN KEY ("user_sourced_id") REFERENCES "public"."users"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "user_resources" ADD CONSTRAINT "user_resources_resource_sourced_id_resources_sourced_id_fk" FOREIGN KEY ("resource_sourced_id") REFERENCES "public"."resources"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "user_roles" ADD CONSTRAINT "user_roles_user_sourced_id_users_sourced_id_fk" FOREIGN KEY ("user_sourced_id") REFERENCES "public"."users"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "user_roles" ADD CONSTRAINT "user_roles_org_sourced_id_orgs_sourced_id_fk" FOREIGN KEY ("org_sourced_id") REFERENCES "public"."orgs"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "users" ADD CONSTRAINT "users_tenant_id_tenants_id_fk" FOREIGN KEY ("tenant_id") REFERENCES "public"."tenants"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "users" ADD CONSTRAINT "users_client_app_id_client_apps_id_fk" FOREIGN KEY ("client_app_id") REFERENCES "public"."client_apps"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "users" ADD CONSTRAINT "users_primary_org_orgs_sourced_id_fk" FOREIGN KEY ("primary_org") REFERENCES "public"."orgs"("sourced_id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "tenant_client_apps" ADD CONSTRAINT "tenant_client_apps_tenant_id_tenants_id_fk" FOREIGN KEY ("tenant_id") REFERENCES "public"."tenants"("id") ON DELETE no action ON UPDATE no action;
ALTER TABLE "tenant_client_apps" ADD CONSTRAINT "tenant_client_apps_client_app_id_client_apps_id_fk" FOREIGN KEY ("client_app_id") REFERENCES "public"."client_apps"("id") ON DELETE no action ON UPDATE no action;
CREATE INDEX "academic_sessions_tenant_id_idx" ON "academic_sessions" USING btree ("tenant_id");
CREATE INDEX "assessment_line_items_tenant_id_idx" ON "assessment_line_items" USING btree ("tenant_id");
CREATE INDEX "assessment_results_tenant_id_idx" ON "assessment_results" USING btree ("tenant_id");
CREATE INDEX "categories_tenant_id_idx" ON "categories" USING btree ("tenant_id");
CREATE INDEX "class_resources_tenant_id_idx" ON "class_resources" USING btree ("tenant_id");
CREATE INDEX "classes_tenant_id_idx" ON "classes" USING btree ("tenant_id");
CREATE INDEX "component_resources_component_sourced_id_idx" ON "component_resources" USING btree ("component_sourced_id");
CREATE INDEX "component_resources_resource_sourced_id_idx" ON "component_resources" USING btree ("resource_sourced_id");
CREATE INDEX "component_resources_tenant_id_idx" ON "component_resources" USING btree ("tenant_id");
CREATE INDEX "course_components_tenant_id_idx" ON "course_components" USING btree ("tenant_id");
CREATE INDEX "course_components_course_sourced_id_idx" ON "course_components" USING btree ("course_sourced_id");
CREATE INDEX "course_resources_tenant_id_idx" ON "course_resources" USING btree ("tenant_id");
CREATE INDEX "courses_tenant_id_idx" ON "courses" USING btree ("tenant_id");
CREATE INDEX "demographics_tenant_id_idx" ON "demographics" USING btree ("tenant_id");
CREATE INDEX "enrollments_tenant_id_idx" ON "enrollments" USING btree ("tenant_id");
CREATE INDEX "learning_objectives_tenant_id_idx" ON "learning_objectives" USING btree ("tenant_id");
CREATE INDEX "line_items_tenant_id_idx" ON "line_items" USING btree ("tenant_id");
CREATE INDEX "orgs_tenant_id_idx" ON "orgs" USING btree ("tenant_id");
CREATE INDEX "resources_tenant_id_idx" ON "resources" USING btree ("tenant_id");
CREATE INDEX "resources_metadata_tenant_id_idx" ON "resources_metadata" USING btree ("tenant_id");
CREATE INDEX "results_tenant_id_idx" ON "results" USING btree ("tenant_id");
CREATE INDEX "score_scales_tenant_id_idx" ON "score_scales" USING btree ("tenant_id");
CREATE INDEX "user_ids_tenant_id_idx" ON "user_ids" USING btree ("tenant_id");
CREATE INDEX "user_resources_tenant_id_idx" ON "user_resources" USING btree ("tenant_id");
CREATE INDEX "users_tenant_id_idx" ON "users" USING btree ("tenant_id");
