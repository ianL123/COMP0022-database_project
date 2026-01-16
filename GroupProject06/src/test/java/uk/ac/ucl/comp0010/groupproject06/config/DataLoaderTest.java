package uk.ac.ucl.comp0010.groupproject06.config;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyList;
import static org.mockito.Mockito.atLeastOnce;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.util.Arrays;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.util.ReflectionTestUtils;
import uk.ac.ucl.comp0010.groupproject06.model.Module;
import uk.ac.ucl.comp0010.groupproject06.model.Student;
import uk.ac.ucl.comp0010.groupproject06.repository.GradesRepository;
import uk.ac.ucl.comp0010.groupproject06.repository.ModuleRepository;
import uk.ac.ucl.comp0010.groupproject06.repository.RegistrationRepository;
import uk.ac.ucl.comp0010.groupproject06.repository.StudentRepository;

/**
 * Test class for the DataLoader component.
 * Tests the functionality of loading sample data into the application.
 */
@SpringBootTest
public class DataLoaderTest {

  @Mock
  private StudentRepository studentRepository;

  @Mock
  private ModuleRepository moduleRepository;

  @Mock
  private GradesRepository gradesRepository;

  @Mock
  private RegistrationRepository registrationRepository;

  @InjectMocks
  private DataLoader dataLoader;

  /**
   * Tests the run method when loadSampleData is set to true.
   * Verifies that all repositories are called to save data.
   *
   * @throws Exception if any error occurs during execution
   */
  @Test
  void testRun_WhenLoadSampleDataIsTrue() throws Exception {
    ReflectionTestUtils.setField(dataLoader, "loadSampleData", true);
    
    // Setup mock data
    Student student = new Student(1L, "John", "Doe", "johndoe", "john@ucl.ac.uk");
    
    // Create at least 8 modules
    List<Module> modules = new ArrayList<>();
    for (int i = 0; i < 8; i++) {
      modules.add(new Module("COMP" + String.format("%04d", i), "Module " + i, true));
    }
    
    when(studentRepository.findAll()).thenReturn(Arrays.asList(student));
    when(moduleRepository.findAll()).thenReturn(modules);
    
    dataLoader.run();
    
    verify(moduleRepository).saveAll(anyList());
    verify(studentRepository).saveAll(anyList());
    verify(registrationRepository, atLeastOnce()).save(any());
    verify(gradesRepository, atLeastOnce()).save(any());
  }

  /**
   * Tests the run method when loadSampleData is set to false.
   * Verifies that no repository methods are called.
   *
   * @throws Exception if any error occurs during execution
   */
  @Test
  void testRun_WhenLoadSampleDataIsFalse() throws Exception {
    ReflectionTestUtils.setField(dataLoader, "loadSampleData", false);
    
    dataLoader.run();
    
    verify(moduleRepository, never()).saveAll(anyList());
    verify(studentRepository, never()).saveAll(anyList());
    verify(registrationRepository, never()).save(any());
    verify(gradesRepository, never()).save(any());
  }
} 