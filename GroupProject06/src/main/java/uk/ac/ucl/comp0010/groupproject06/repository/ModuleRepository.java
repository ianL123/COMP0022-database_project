package uk.ac.ucl.comp0010.groupproject06.repository;

import java.util.Optional;
import org.springframework.data.repository.CrudRepository;
import org.springframework.stereotype.Repository;
import uk.ac.ucl.comp0010.groupproject06.model.Module;

/**
 * Repository for the Module model.
 */
@Repository
public interface ModuleRepository extends CrudRepository<Module, String> {
  Optional<Module> findByCode(String code);
} 