package uk.ac.ucl.comp0010.groupproject06.repository;

import org.springframework.data.repository.CrudRepository;
import org.springframework.stereotype.Repository;
import uk.ac.ucl.comp0010.groupproject06.model.Registration;

/**
 * Repository for the Registration entity.
 */
@Repository
public interface RegistrationRepository extends CrudRepository<Registration, Long> {
  boolean existsByStudentIdAndModuleCode(Long studentId, String moduleCode);
}
