//
// Regenerate .ssh/authorized_keys files.  Must be setuid root.
//
#include "run.h"

MAIN("regenerate_ssh_authorized_keys.py")

int is_trusted_user(uid_t uid)
{
    return (uid == ROOT_UID) || (uid == WWW_DATA_UID);
}
