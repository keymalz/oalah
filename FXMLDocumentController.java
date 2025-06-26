package TableView;



import java.io.IOException;
import java.net.URL;
import java.util.ResourceBundle;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.fxml.Initializable;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.TableColumn;
import javafx.scene.control.TableView;
import javafx.scene.control.TextField;
import javafx.scene.control.cell.PropertyValueFactory;
import javafx.stage.Stage;

public class FXMLDocumentController implements Initializable {

    // Komponen untuk TableView
    @FXML
    private TableView<Student> tvStudent;
    @FXML
    private TableColumn<Student, String> tcNim;
    @FXML
    private TableColumn<Student, String> tcNama;
    @FXML
    private TextField tfNimBaru;
    @FXML
    private TextField tfNamaBaru;

    // Model untuk daftar mahasiswa
    private Studentlist dataMahasiswa;

    @Override
    public void initialize(URL url, ResourceBundle rb) {
        // Menghubungkan kolom tabel ke properti di kelas Student
        tcNim.setCellValueFactory(new PropertyValueFactory<>("nim"));
        tcNama.setCellValueFactory(new PropertyValueFactory<>("name"));

        // Membuat dan mengisi data awal ke dalam tabel
        dataMahasiswa = new Studentlist();
        dataMahasiswa.setDummy();
        tvStudent.setItems(dataMahasiswa.get());
    }

    // Method untuk tombol "Tambah"
    @FXML
    private void tambahButtonAction(ActionEvent event) {
        // Mengambil data dari TextField
        String nim = tfNimBaru.getText();
        String nama = tfNamaBaru.getText();

        // Menambahkan data baru ke dalam list
        dataMahasiswa.add(new Student(nim, nama));

        tfNimBaru.clear();
        tfNamaBaru.clear();
    }

    // Method untuk tombol "Buka Jendela 2"
    @FXML
    private void bukaJendelaBaruAction(ActionEvent event) throws IOException {
        // Logika untuk memuat FXML baru dan menampilkannya di Stage baru
        Parent root = FXMLLoader.load(getClass().getResource("FXMLStage2.fxml"));
        Scene scene = new Scene(root);
        Stage stage = new Stage();
        stage.setTitle("Jendela Baru");
        stage.setScene(scene);
        stage.show();
    }
}