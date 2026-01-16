package uk.ac.ucl.comp0010.groupproject06.controller;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.when;

import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.springframework.http.ResponseEntity;
import uk.ac.ucl.comp0010.groupproject06.model.Module;
import uk.ac.ucl.comp0010.groupproject06.repository.ModuleRepository;

/**
 * Test class for the ModuleController.
 * Tests the REST endpoints for module management operations.
 */
public class ModuleControllerTest {

  @Mock
  private ModuleRepository moduleRepository;

  @InjectMocks
  private ModuleController moduleController;

  /**
   * Sets up the test environment before each test.
   * Initializes mock objects.
   */
  @BeforeEach
  void setUp() {
    MockitoAnnotations.openMocks(this);
  }

  /**
   * Tests the endpoint for retrieving all modules.
   * Verifies that the endpoint returns the correct list of modules.
   */
  @Test
  void testGetAllModules() {
    List<Module> modules = Arrays.asList(
      new Module("COMP0010", "Software Engineering", true),
      new Module("COMP0011", "Database Systems", false)
    );

    when(moduleRepository.findAll()).thenReturn(modules);

    ResponseEntity<List<Module>> response = moduleController.getAllModules();
    assertEquals(200, response.getStatusCodeValue());
    assertEquals(2, response.getBody().size());
  }

  /**
   * Tests the successful update of a module.
   * Verifies that the endpoint returns the updated module with a 200 status code.
   */
  @Test
  void testUpdateModule_Success() {
    String code = "COMP0010";
    Module existingModule = new Module(code, "Software Engineering", true);
    Module updatedModule = new Module(code, "Advanced Software Engineering", false);

    when(moduleRepository.findById(code)).thenReturn(Optional.of(existingModule));

    ResponseEntity<Module> response = moduleController.updateModule(code, updatedModule);
    assertEquals(200, response.getStatusCodeValue());
  }

  /**
   * Tests the update of a non-existent module.
   * Verifies that the endpoint returns a 404 status code when the module is not found.
   */
  @Test
  void testUpdateModule_NotFound() {
    String code = "COMP0010";
    Module updatedModule = new Module(code, "Software Engineering", true);

    when(moduleRepository.findById(code)).thenReturn(Optional.empty());

    ResponseEntity<Module> response = moduleController.updateModule(code, updatedModule);
    assertEquals(404, response.getStatusCodeValue());
  }
} 