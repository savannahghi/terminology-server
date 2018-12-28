export DATABASE_URL=postgres://snomed:snomed@localhost:5432/snomed_search_v2
export APP_SETTINGS='snomedct_terminology_server.config.config.DevelopmentConfig'
export MIGRATIONS_PATH=snomedct_terminology_server/migrations
alias db='python manage.py db'
export STATIC_ROOT=/opt/snomedct_terminology_server/static/
alias s='snomed_manage shell'
alias spnb='snomed_manage shell_plus --notebook'
export ADJACENCY_LIST_FILE='.concept_subsumption.adjlist'
export DEBUG=true
export ISO_639_CODES='iso_639_2.json'
export NEW_RELIC_CONFIG_FILE=~/savannahinformatics/slade360-terminology-server/terminology_server/newrelic.ini
export NEW_RELIC_ENVIRONMENT=development
export API_ROOT_ENDPOINT='http://snomed-20160731-release-server-2016-10-10.slade360emr.com'

