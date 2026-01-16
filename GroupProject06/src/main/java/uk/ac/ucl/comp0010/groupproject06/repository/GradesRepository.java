package uk.ac.ucl.comp0010.groupproject06.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import uk.ac.ucl.comp0010.groupproject06.model.Grade;

/**
 * Repository for handling grade data.
 */
public interface GradesRepository extends JpaRepository<Grade, Long> {
} 