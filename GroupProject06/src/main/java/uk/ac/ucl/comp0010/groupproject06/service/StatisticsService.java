package uk.ac.ucl.comp0010.groupproject06.service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import uk.ac.ucl.comp0010.groupproject06.exception.NoGradeAvailableException;
import uk.ac.ucl.comp0010.groupproject06.model.Module;
import uk.ac.ucl.comp0010.groupproject06.model.Student;
import uk.ac.ucl.comp0010.groupproject06.repository.ModuleRepository;
import uk.ac.ucl.comp0010.groupproject06.repository.StudentRepository;

/**
 * Service class for  the statistics page (extension).
 */
@Service
public class StatisticsService {

  @Autowired
  private StudentRepository studentRepository;

  @Autowired
  private ModuleRepository moduleRepository;

  /**
   * Returns a Map of type String, Double. 
   * This is a list of Students and their corresponding average grade.
   */
  public Map<String, Double> getAverageGradePerStudent() {
    List<Student> students = studentRepository.findAll();
    Map<String, Double> studentAverageGrades = new HashMap<>();

    for (Student student : students) {
      try {
        double average = student.computeAverage(); // Method may throw NoGradeAvailableException
        String fullName = student.getFirstName() + " " + student.getLastName(); // Full name
        
        studentAverageGrades.put(fullName, average);
      } catch (NoGradeAvailableException e) {
        // Handle the case where no grades are available
        String fullName = student.getFirstName() + " " + student.getLastName();
        studentAverageGrades.put(fullName, null); // Or assign a default value like 0.0 or "N/A"
      }
    }

    return studentAverageGrades;
  }

  /**
   * Returns a Map of type String, Double.
   * This is a list of Modules and their corresponding average grade.
   */
  public Map<String, Double> getAverageGradePerModule() {
    Iterable<Module> modules = moduleRepository.findAll();
    Map<String, Double> moduleAverageGrades = new HashMap<>();

    for (Module module : modules) {
      try {
        double average = module.computeAverageGrade();
        String moduleName = module.getCode() + " - " + module.getName();
        moduleAverageGrades.put(moduleName, average);
      } catch (NoGradeAvailableException e) {
        // Handle the case where no grades are available
        String moduleName = module.getCode() + " - " + module.getName();
        moduleAverageGrades.put(moduleName, null);
      }
    }

    return moduleAverageGrades;
  }
}