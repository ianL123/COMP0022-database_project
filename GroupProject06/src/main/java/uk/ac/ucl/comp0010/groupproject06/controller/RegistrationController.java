package uk.ac.ucl.comp0010.groupproject06.controller;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import uk.ac.ucl.comp0010.groupproject06.model.Module;
import uk.ac.ucl.comp0010.groupproject06.model.Registration;
import uk.ac.ucl.comp0010.groupproject06.model.Student;
import uk.ac.ucl.comp0010.groupproject06.repository.ModuleRepository;
import uk.ac.ucl.comp0010.groupproject06.repository.RegistrationRepository;
import uk.ac.ucl.comp0010.groupproject06.repository.StudentRepository;
import uk.ac.ucl.comp0010.groupproject06.request.RegistrationRequest;

/**
 * Controller for handling registration requests.
 */
@RestController
@RequestMapping("/registrations")
public class RegistrationController {

  @Autowired
  private RegistrationRepository registrationRepository;

  @Autowired
  private StudentRepository studentRepository;

  @Autowired
  private ModuleRepository moduleRepository;

  /**
   * Register a student to a module.
   *
   * @param request The registration request.
   * @return A response entity with the status code.
   */
  @PostMapping
  public ResponseEntity<String> registerStudentToModule(@RequestBody RegistrationRequest request) {
    Long studentId = request.getStudentId();
    String moduleCode = request.getModuleCode();

    Optional<Student> studentOpt = studentRepository.findById(studentId);
    Optional<Module> moduleOpt = moduleRepository.findByCode(moduleCode);

    if (studentOpt.isPresent() && moduleOpt.isPresent()) {
      // Check if the student is already registered for the module
      if (registrationRepository.existsByStudentIdAndModuleCode(studentId, moduleCode)) {
        return ResponseEntity.status(409).body("Student is already registered for this module.");
      }
      
      Registration registration = new Registration(moduleOpt.get(), studentOpt.get());
      registrationRepository.save(registration);
      return ResponseEntity.status(201).build(); // Created
    } else {
      return ResponseEntity.status(404).body("Student or Module not found."); // Not Found
    }
  }

  /**
   * Get the list of all registrations.
   *
   * @return A response entity with the list of registrations.
   */
  @GetMapping
  public ResponseEntity<List<Registration>> getAllRegistrations() {
    List<Registration> registrations = 
        StreamSupport.stream(registrationRepository.findAll().spliterator(), false)
        .collect(Collectors.toList());
    return ResponseEntity.ok(registrations);
  }
}
