package grader;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.io.IOException;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.ArrayList;
import java.util.List;

class StructureTest {

    private static final Path ROOT = Path.of(System.getProperty("user.dir"));
    private static final Path SRC = ROOT.resolve("src/main/java");
    private static final Path TEST = ROOT.resolve("src/test/java");

    @Test
    void testSrcHasJavaFiles() throws IOException {
        List<Path> files = findFiles(SRC, ".java");
        assertFalse(files.isEmpty(), "No .java files found in src/main/java");
    }

    @Test
    void testHasSpringBootApplication() throws IOException{
        List<Path> files = findFiles(SRC, ".java");
        boolean hasAnnotation = files.stream().anyMatch(f -> {
                try{
                    return Files.readString(f).contains("@SpringBootApplication");
                }catch(IOException e) { return false; }
        });

        assertTrue(hasAnnotation, "No class with @SpringBootApplication found in src/main/java");
    }

    @Test
    void testHasController() throws IOException {
          List<Path> files = findFiles(SRC, ".java");
          boolean hasController = files.stream().anyMatch(f -> {
              try {
                  String content = Files.readString(f);
                  return content.contains("@RestController") || content.contains("@Controller");
              } catch (IOException e) { return false; }
          });
          assertTrue(hasController, "No class with @RestController or @Controller found");
    }

    @Test
    void testHasStudentTests() throws IOException {
        List<Path> files = findFiles(TEST, ".java");
        boolean hasTests = files.stream().anyMatch(f -> {
        try {
            return Files.readString(f).contains("@Test");
        } catch (IOException e) { return false; }
        });
        assertTrue(hasTests, "No test files with @Test found in src/test/java/");
    }

    private List<Path> findFiles(Path dir, String extension) throws IOException {
      List<Path> result = new ArrayList<>();
      if (!Files.exists(dir)) return result;
      Files.walkFileTree(dir, new SimpleFileVisitor<>() {
          @Override
          public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) {
              if (file.toString().endsWith(extension)) result.add(file);
              return FileVisitResult.CONTINUE;
          }
      });
      return result;
    }

}