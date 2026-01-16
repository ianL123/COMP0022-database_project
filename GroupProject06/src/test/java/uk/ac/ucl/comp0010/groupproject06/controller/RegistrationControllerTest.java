package uk.ac.ucl.comp0010.groupproject06.controller;

import java.util.List;
import java.util.ArrayList;
import org.junit.jupiter.api.BeforeEach;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.when;

import java.util.Collections;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.springframework.http.ResponseEntity;
import uk.ac.ucl.comp0010.groupproject06.model.Module;
import uk.ac.ucl.comp0010.groupproject06.model.Registration;
import uk.ac.ucl.comp0010.groupproject06.model.Student;
import uk.ac.ucl.comp0010.groupproject06.repository.ModuleRepository;
import uk.ac.ucl.comp0010.groupproject06.repository.RegistrationRepository;
import uk.ac.ucl.comp0010.groupproject06.repository.StudentRepository;
import uk.ac.ucl.comp0010.groupproject06.request.RegistrationRequest;

/**
 * Test class for the RegistrationController.
 * Tests the REST endpoints for managing student module registrations.
 */
public class RegistrationControllerTest {

  @Mock
  private RegistrationRepository registrationRepository;

  @Mock
  private StudentRepository studentRepository;

  @Mock
  private ModuleRepository moduleRepository;

  @InjectMocks
  private RegistrationController registrationController;

  /**
   * Sets up the test environment before each test.
   * Initializes mock objects.
   *
   * @throws Exception if mock initialization fails
   */
  @BeforeEach
  void setUp() throws Exception {
    MockitoAnnotations.openMocks(this);
  }

  /**
   * Tests successful registration of a student to a module.
   * Verifies that the endpoint returns a 201 status code when registration is successful.
   */
  @Test
  void testRegisterStudentToModule() {
    Long studentId = 1L;
    String moduleCode = "COMP0010";
    Student student = new Student(studentId, "John", "Doe", "johndoe", "john@ucl.ac.uk");
    Module module = new Module(moduleCode, "Software Engineering", true);
    RegistrationRequest request = new RegistrationRequest(studentId, moduleCode);

    when(studentRepository.findById(studentId)).thenReturn(Optional.of(student));
    when(moduleRepository.findByCode(moduleCode)).thenReturn(Optional.of(module));

    ResponseEntity<String> response = registrationController.registerStudentToModule(request);
    assertEquals(201, response.getStatusCodeValue());
  }

  /**
   * Tests registration when neither student nor module exists.
   * Verifies that the endpoint returns a 404 status code.
   */
  @Test
  void testRegisterStudentToModule_NotFound() {
    Long studentId = 1L;
    String moduleCode = "COMP0010";
    RegistrationRequest request = new RegistrationRequest(studentId, moduleCode);

    when(studentRepository.findById(studentId)).thenReturn(Optional.empty());
    when(moduleRepository.findByCode(moduleCode)).thenReturn(Optional.empty());

    ResponseEntity<String> response = registrationController.registerStudentToModule(request);
    assertEquals(404, response.getStatusCodeValue());
  }

  /**
   * Tests registration when student exists but module does not.
   * Verifies that the endpoint returns a 404 status code.
   */
  @Test
  void testRegisterStudentToModule_ModuleNotFound() {
    Long studentId = 1L;
    String moduleCode = "COMP0010";
    Student student = new Student(studentId, "John", "Doe", "johndoe", "john@ucl.ac.uk");
    RegistrationRequest request = new RegistrationRequest(studentId, moduleCode);

    when(studentRepository.findById(studentId)).thenReturn(Optional.of(student));
    when(moduleRepository.findByCode(moduleCode)).thenReturn(Optional.empty());

    ResponseEntity<String> response = registrationController.registerStudentToModule(request);
    assertEquals(404, response.getStatusCodeValue());
  }

  /**
 * Tests registration when student is already registered for the module.
 * Verifies that the endpoint returns a 409 status code.
 */
  @Test
  void testRegisterStudentToModule_AlreadyRegistered() {
      Long studentId = 1L;
      String moduleCode = "COMP0010";
      Student student = new Student(studentId, "John", "Doe", "johndoe", "john@ucl.ac.uk");
      Module module = new Module(moduleCode, "Software Engineering", true);
      RegistrationRequest request = new RegistrationRequest(studentId, moduleCode);

      when(studentRepository.findById(studentId)).thenReturn(Optional.of(student));
      when(moduleRepository.findByCode(moduleCode)).thenReturn(Optional.of(module));
      when(registrationRepository.existsByStudentIdAndModuleCode(studentId, moduleCode)).thenReturn(true);

      ResponseEntity<String> response = registrationController.registerStudentToModule(request);
      assertEquals(409, response.getStatusCodeValue());
  }

  /**
   * Tests successful retrieval of all registrations.
   * Verifies that the endpoint returns a 200 status code and the list of registrations.
   */
  @Test
  void testGetAllRegistrations() {
      List<Registration> registrations = new ArrayList<>();
      registrations.add(new Registration(new Module("COMP0010", "Software Engineering", true), new Student(1L, "John", "Doe", "johndoe", "john@ucl.ac.uk")));
      
      when(registrationRepository.findAll()).thenReturn(registrations);

      ResponseEntity<List<Registration>> response = registrationController.getAllRegistrations();
      assertEquals(200, response.getStatusCodeValue());
      assertEquals(1, response.getBody().size());
  }

  /**
   * Tests retrieval of all registrations when none exist.
   * Verifies that the endpoint returns a 200 status code and an empty list.
   */
  @Test
  void testGetAllRegistrations_Empty() {
      when(registrationRepository.findAll()).thenReturn(Collections.emptyList());

      ResponseEntity<List<Registration>> response = registrationController.getAllRegistrations();
      assertEquals(200, response.getStatusCodeValue());
      assertEquals(0, response.getBody().size());
  }
}