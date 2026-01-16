package uk.ac.ucl.comp0010.groupproject06.controller;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.util.HashMap;
import java.util.Map;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import uk.ac.ucl.comp0010.groupproject06.service.StatisticsService;

/**
 * Test class for the StatisticsController.
 * Tests the REST endpoints related to student and module statistics.
 */
@SpringBootTest
@AutoConfigureMockMvc
public class StatisticsControllerTest {

  @Autowired
  private MockMvc mockMvc;

  @MockBean
  private StatisticsService statisticsService;

  private Map<String, Double> averageGrades;
  private Map<String, Double> moduleAverages;

  /**
   * Sets up test data before each test.
   * Initializes maps of student names and module names to their average grades.
   */
  @BeforeEach
  void setUp() {
    averageGrades = new HashMap<>();
    averageGrades.put("John Doe", 85.0);
    averageGrades.put("Jane Smith", 90.0);

    moduleAverages = new HashMap<>();
    moduleAverages.put("COMP0010 - Software Engineering", 87.5);
    moduleAverages.put("COMP0011 - Database Systems", 82.0);
  }

  /**
   * Tests the endpoint for retrieving average grades per student.
   * Verifies that the endpoint returns correct data in JSON format.
   *
   * @throws Exception if any error occurs during the mock request
   */
  @Test
  void testGetAverageGradePerStudent() throws Exception {
    when(statisticsService.getAverageGradePerStudent()).thenReturn(averageGrades);

    mockMvc.perform(get("/statistics/average/student"))
      .andExpect(status().isOk())
      .andExpect(content().contentType(MediaType.APPLICATION_JSON))
      .andExpect(content().json("{'John Doe': 85.0, 'Jane Smith': 90.0}"));
  }

  /**
   * Tests the endpoint for retrieving average grades when no student data exists.
   * Verifies that the endpoint returns an empty JSON object.
   *
   * @throws Exception if any error occurs during the mock request
   */
  @Test
  void testGetAverageGradePerStudentWithEmptyData() throws Exception {
    when(statisticsService.getAverageGradePerStudent()).thenReturn(new HashMap<>());

    mockMvc.perform(get("/statistics/average/student"))
      .andExpect(status().isOk())
      .andExpect(content().contentType(MediaType.APPLICATION_JSON))
      .andExpect(content().json("{}"));
  }

  /**
   * Tests the endpoint for retrieving average grades per module.
   * Verifies that the endpoint returns correct data in JSON format.
   *
   * @throws Exception if any error occurs during the mock request
   */
  @Test
  void testGetAverageGradePerModule() throws Exception {
    when(statisticsService.getAverageGradePerModule()).thenReturn(moduleAverages);

    mockMvc.perform(get("/statistics/average/module"))
      .andExpect(status().isOk())
      .andExpect(content().contentType(MediaType.APPLICATION_JSON))
      .andExpect(content().json(
        "{'COMP0010 - Software Engineering': 87.5, 'COMP0011 - Database Systems': 82.0}"
      ));
  }

  /**
   * Tests the endpoint for retrieving average grades when no module data exists.
   * Verifies that the endpoint returns an empty JSON object.
   *
   * @throws Exception if any error occurs during the mock request
   */
  @Test
  void testGetAverageGradePerModuleWithEmptyData() throws Exception {
    when(statisticsService.getAverageGradePerModule()).thenReturn(new HashMap<>());

    mockMvc.perform(get("/statistics/average/module"))
      .andExpect(status().isOk())
      .andExpect(content().contentType(MediaType.APPLICATION_JSON))
      .andExpect(content().json("{}"));
  }
} 