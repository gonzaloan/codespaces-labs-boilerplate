package grader;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.io.IOException;
import java.nio.file.Path;

class ExecutionTest {

  private static final Path ROOT = Path.of(System.getProperty("user.dir"));

  @Test
  void testStudentTestsPass() throws IOException, InterruptedException {
      ProcessBuilder pb = new ProcessBuilder("mvn", "test", "-q")
          .directory(ROOT.toFile())
          .redirectErrorStream(true);

      Process process = pb.start();
      String output = new String(process.getInputStream().readAllBytes());
      int exitCode = process.waitFor();

      assertEquals(0, exitCode,
          "Student tests failed. Run `mvn test` locally to see the errors.\n" + output.lines()
              .filter(l -> l.contains("ERROR") || l.contains("FAILED") || l.contains("Tests run"))
              .reduce("", (a, b) -> a + "\n" + b));
  }

  @Test
  void testProjectBuildsWithoutErrors() throws IOException, InterruptedException {
      ProcessBuilder pb = new ProcessBuilder("mvn", "compile", "-q")
          .directory(ROOT.toFile())
          .redirectErrorStream(true);

      Process process = pb.start();
      String output = new String(process.getInputStream().readAllBytes());
      int exitCode = process.waitFor();

      assertEquals(0, exitCode,
          "Project does not compile. Fix build errors before pushing.\n" + output);
  }
}
