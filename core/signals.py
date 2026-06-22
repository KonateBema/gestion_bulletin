@receiver(post_save, sender=User)
def create_profile_and_etudiant(sender, instance, created, **kwargs):

    if created:

        Profile.objects.create(user=instance, role='ETUDIANT')

        classe = Classe.objects.first()

        if classe:  # ✅ sécurité
            Etudiant.objects.create(
                user=instance,
                matricule=f"ETU{instance.id:04d}",
                date_naissance="2000-01-01",
                sexe="M",
                telephone="0000000000",
                classe=classe
            )