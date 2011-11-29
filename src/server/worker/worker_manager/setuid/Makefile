TARGETS=run_delete_application run_deploy run_start run_stop run_retrieve_logs

all: $(TARGETS)
	-chown root.djangy $(TARGETS)
	chmod 6710 $(TARGETS)

clean:
	rm -f $(TARGETS) *~
