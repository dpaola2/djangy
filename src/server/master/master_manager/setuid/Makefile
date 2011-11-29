TARGETS=run_add_application run_add_ssh_public_key run_allocate run_command run_configure_proxycache run_delete_application run_deploy run_regenerate_ssh_authorized_keys run_remove_ssh_public_key run_retrieve_logs run_shell_serve

all: $(TARGETS)
	-chown root.djangy $(TARGETS)
	chmod 6710 $(TARGETS)

clean:
	rm -f $(TARGETS) *~
