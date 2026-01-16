package uk.ac.ucl.comp0010.groupproject06.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import uk.ac.ucl.comp0010.groupproject06.model.Student;

/**
 * Repository for handling student data.
 */
public interface StudentRepository extends JpaRepository<Student, Long> {
}
