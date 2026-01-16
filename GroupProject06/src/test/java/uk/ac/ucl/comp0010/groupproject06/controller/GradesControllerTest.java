package uk.ac.ucl.comp0010.groupproject06.controller;

import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import uk.ac.ucl.comp0010.groupproject06.repository.GradesRepository;
import uk.ac.ucl.comp0010.groupproject06.repository.ModuleRepository;
import uk.ac.ucl.comp0010.groupproject06.repository.StudentRepository;

class GradesControllerTest {
    @Mock
    private GradesRepository gradesRepository;

    @Mock
    private StudentRepository studentRepository;

    @Mock
    private ModuleRepository moduleRepository;

    @InjectMocks
    private GradesController gradesController;

    GradesControllerTest() {
        MockitoAnnotations.openMocks(this);
    }

    }
