TARGETS=run_clear_cache run_configure run_delete_application

all: $(TARGETS)
	-chown root.djangy $(TARGETS)
	chmod 6710 $(TARGETS)

clean:
	rm -f $(TARGETS) *~
