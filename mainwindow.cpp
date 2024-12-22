#include "mainwindow.h"
#include "./ui_mainwindow.h"

void delay(int ms)
{
    QTime dieTime= QTime::currentTime().addMSecs(ms);
    while (QTime::currentTime() < dieTime)
        QCoreApplication::processEvents(QEventLoop::AllEvents, 100);
}

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
{
    ui->setupUi(this);

    ui->SampleRateBox->addItem("2 MHz");
    ui->SampleRateBox->addItem("8 MHz");
    ui->SampleRateBox->addItem("10 MHz");
    ui->SampleRateBox->addItem("12.5 MHz");
    ui->SampleRateBox->addItem("16 MHz");
    ui->SampleRateBox->addItem("20 MHz");

    ui->GainEdit->setEnabled(true);
    ui->AnaliseButton->setEnabled(true);

    portInfos = QSerialPortInfo::availablePorts();

    for(const QSerialPortInfo& info : portInfos)
    {
        ui->SerialPortBox->addItem(info.portName() + " (" + info.description() + ")");
    }

    int w = ui->label->pixmap().width();
    int h = ui->label->pixmap().height();
    ui->label->setPixmap(ui->label->pixmap().scaled(w, h, Qt::KeepAspectRatio));

    ui->centralwidget->setLayout(ui->verticalLayout);

    connect(ui->SDRFileButton, &QToolButton::pressed, this, &MainWindow::sdrFDialog);
    connect(ui->AnaliseButton, &QPushButton::pressed, this, &MainWindow::analiseButtonPress);
    connect(ui->SyncFileButton, &QToolButton::pressed, this, &MainWindow::syncFDialog);
    connect(ui->GRAFileButton, &QToolButton::pressed, this, &MainWindow::graFDialog);
    connect(ui->OutPropFileButton, &QToolButton::pressed, this, &MainWindow::outFDialog);
    connect(ui->RunButton, &QPushButton::pressed, this, &MainWindow::runButtonPress);
    connect(&(this->plotproc), &QProcess::finished, this, &MainWindow::plotprocFinishedSlot);
}

void MainWindow::sdrFDialog()
{
    QString filename = QFileDialog::getOpenFileName(this, tr("Open File"), "C:\\", tr("SDR Sequence (*.bin)"));
    ui->SDRFileEdit->setText(filename);
}

void MainWindow::syncFDialog()
{
    QString filename = QFileDialog::getOpenFileName(this, tr("Open File"), "C:\\", tr("Synchronization sequence (*.xml)"));
    ui->SyncFileEdit->setText(filename);
}

void MainWindow::graFDialog()
{
    QString filename = QFileDialog::getOpenFileName(this, tr("Open File"), "C:\\", tr("GRA Sequence (*.txt)"));
    ui->GRAFileEdit->setText(filename);
}

void MainWindow::outFDialog()
{
    QString filename = QFileDialog::getOpenFileName(this, tr("Open File"), "C:\\", tr("Out Properties file (*.bin)"));
    ui->OutPropFileEdit->setText(filename);
}

int MainWindow::runButtonPress()
{
    QProcess syncproc, graproc, hackrfproc, picoproc;
    QStringList syncargs, graargs, hackrfargs, picoargs;
    bool warn = false;

    if(ui->SyncFileEdit->text() != "" || ui->GRAFileEdit->text() != "" || ui->SDRFileEdit->text() != "" || ui->OutPropFileEdit->text() != "")
    {
        syncargs << ui->SyncFileEdit->text();
        graargs << ui->GRAFileEdit->text();

        hackrfargs << "-t" << ui->SDRFileEdit->text();
        hackrfargs << "-f" << ui->FreqBox->text();
        hackrfargs << "-a" << (ui->AmplCheck->isChecked() ? QString("0") : QString("1"));
        hackrfargs << "-x" << ui->GainEdit->text();

        picoargs << ui->OutPropFileEdit->text();
    }
    else
    {
        QMessageBox::warning(this, tr("LMRIgui App"), tr("Please, enter all file destinations!"));
        warn = true;
    }

    if(!warn)
    {
        //QProgressDialog progress("Running program...", "Abort", 0, 100, this);
        //progress.setWindowModality(Qt::WindowModal);
        //progress.setValue(0);

        if(ui->SyncDebugModeCheck->isChecked())
        {
            syncargs << "--debug";
        }
        if(ui->SyncDisConCheck->isChecked())
        {
            syncargs << "--disable-console";
        }

        QString pnum = portInfos[ui->SerialPortBox->currentIndex()].portName().mid(3);
        syncargs << "-p" << pnum;

        if(ui->GRADebugModeCheck->isChecked())
        {
            graargs << "--debug";
        }
        if(ui->GRADisConCheck->isChecked())
        {
            graargs << "--disable-console";
        }

        if(ui->OutPropDebugModeCheck->isChecked())
            picoargs << "--debug";

        syncproc.start(QDir::currentPath() + QString("\\Sync.exe"), syncargs);

        if(!syncproc.waitForStarted())
        {
            QMessageBox::critical(this, tr("LMRIgui App"), tr(QDir::currentPath().toStdString().c_str()));
            return -11;
        }

        if (!syncproc.waitForFinished())
        {
            QMessageBox::critical(this, tr("LMRIgui App"), tr("Sync not finished!"));
            return -11;
        }

        syncproc.close();

        switch(syncproc.exitCode())
        {
        case -1:
            QMessageBox::critical(this, tr("LMRIgui App"), tr("Wrong arguments for sync!"));
            return -1;
            break;
        case -2:
            QMessageBox::critical(this, tr("LMRIgui App"), tr("Wrong serial port number!"));
            return -2;
            break;
        case -5:
            QMessageBox::critical(this, tr("LMRIgui App"), tr("Wrong sync-file structure!"));
            return -5;
            break;
        case -6:
            QMessageBox::critical(this, tr("LMRIgui App"), tr("No connection to serial port in Sync.exe!"));
        }

        //progress.setValue(12);

        //QMessageBox::information(this, tr("LMRIgui App"), tr("Sync finished!"));


        QSerialPort* syncport(new QSerialPort(this));
        syncport->setPortName(portInfos[ui->SerialPortBox->currentIndex()].portName());
        syncport->setBaudRate(QSerialPort::Baud9600);
        syncport->setDataBits(QSerialPort::Data8);
        syncport->setParity(QSerialPort::NoParity);
        syncport->setStopBits(QSerialPort::OneStop);
        syncport->setFlowControl(QSerialPort::NoFlowControl);


        //if(!syncport->open(QIODevice::ReadWrite))
        //{
        //    QMessageBox::critical(this, tr("LMRIgui App"), tr((syncport->portName() + QString(" have not connected!")).toStdString().c_str()));
        //    return -2;
        //}

        //QByteArray data;
        //bool err = false;

        if(!syncport->open(QIODevice::ReadWrite))
        {
            QMessageBox::critical(this, tr("LMRIgui App"), tr((syncport->portName() + QString(" cannot be connected!")).toStdString().c_str()));
            return -3;
        }

        while(syncport->isOpen())
        {
            if(!syncport->write("e"))
            {
                QMessageBox::critical(this, tr("LMRIgui App"), tr("Cannot send data to serial port!"));
                return -4;
            };
            syncport->close();
        }

        //progress.setValue(25);

        graproc.start(QDir::currentPath() + QString("\\UDP_test.exe"), graargs);

        if(!graproc.waitForStarted())
        {
            QMessageBox::critical(this, tr("LMRIgui App"), tr("GRA programm not started"));
            return -7;
        }

        if (!graproc.waitForFinished())
        {
            QMessageBox::critical(this, tr("LMRIgui App"), tr("GRA programm not finished!"));
            return -7;
        }

        graproc.close();
        //progress.setValue(50);


        picoproc.start(QDir::currentPath() + QString("\\pico_test_00.exe"), picoargs);

        if(!picoproc.waitForStarted())
        {
            QMessageBox::critical(this, tr("LMRIgui App"), tr("Pico programm not started"));
            return -8;
        }

        delay(3000);
        //progress.setValue(75);

        hackrfproc.start(QDir::currentPath() + QString("\\hackrftrans00.exe"), hackrfargs);

        if(!hackrfproc.waitForStarted())
        {
            QMessageBox::critical(this, tr("LMRIgui App"), tr("SDR programm not started"));
            return -9;
        }

        if (!hackrfproc.waitForFinished())
        {
            QMessageBox::critical(this, tr("LMRIgui App"), tr("SDR programm not finished!"));
            return -9;
        }

        hackrfproc.close();

        if(!picoproc.waitForFinished())
        {
            QMessageBox::critical(this, tr("LMRIgui App"), tr("Pico programm not finished!"));
            return -8;
        }

        picoproc.close();

        //if(data.isEmpty())
        //{
        //    QMessageBox::critical(this, tr("LMRIgui App"), tr("No data from serial port!"));
        //    syncport->close();
        //     return -3;
        //}


    }

    return 0;
}

int MainWindow::analiseButtonPress()
{
    QStringList plotargs;

    plotargs << QDir::currentPath() + QString("\\plot.py");
    plotproc.start("python", plotargs);

    return 0;
}

void MainWindow::plotprocFinishedSlot()
{
    plotproc.close();
}

MainWindow::~MainWindow()
{
    delete ui;
}
