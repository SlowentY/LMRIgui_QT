#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QImage>
#include <QFileDialog>
#include <QSerialPortInfo>
#include <QSerialPort>
#include <QProcess>
#include <QDir>
#include <QObject>
#include <QMessageBox>
#include <QProgressDialog>
#include <QTime>

QT_BEGIN_NAMESPACE

void delay(int ms);

namespace Ui {
class MainWindow;
}
QT_END_NAMESPACE

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private slots:
    void sdrFDialog();
    void syncFDialog();
    void graFDialog();
    void outFDialog();
    int runButtonPress();
    int analiseButtonPress();
    void plotprocFinishedSlot();

private:
    Ui::MainWindow *ui;
    QList<QSerialPortInfo> portInfos;
    QProcess plotproc;
};
#endif // MAINWINDOW_H
