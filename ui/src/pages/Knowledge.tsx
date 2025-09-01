import { useState } from 'react';
import { ArrowLeft, Upload, FileText, Globe, Database } from 'lucide-react';
import { cn } from '../utils/cn';

type DataSourceType = 'text' | 'notion' | 'web';

interface StepIndicatorProps {
  currentStep: number;
  steps: { label: string; step: number }[];
}

function StepIndicator({ currentStep, steps }: StepIndicatorProps) {
  return (
    <div className="flex items-center gap-4 mb-8">
      {steps.map((step, index) => (
        <div key={step.step} className="flex items-center">
          <div className="flex items-center gap-2">
            <div className={cn(
              "flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium",
              step.step === currentStep 
                ? "bg-blue-500 text-white" 
                : step.step < currentStep 
                ? "bg-gray-300 text-gray-600"
                : "bg-gray-200 text-gray-500"
            )}>
              <span className="text-xs">STEP {step.step}</span>
            </div>
            <span className={cn(
              "text-sm font-medium",
              step.step === currentStep ? "text-blue-600" : "text-gray-600"
            )}>
              {step.label}
            </span>
          </div>
          {index < steps.length - 1 && (
            <div className="w-8 h-px bg-gray-300 mx-4" />
          )}
        </div>
      ))}
    </div>
  );
}

interface DataSourceTabProps {
  type: DataSourceType;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  isActive: boolean;
  onClick: () => void;
}

function DataSourceTab({ type, label, icon: Icon, isActive, onClick }: DataSourceTabProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "flex items-center gap-3 px-6 py-4 border rounded-lg transition-all",
        isActive 
          ? "border-blue-500 bg-blue-50 text-blue-700" 
          : "border-gray-300 bg-white text-gray-700 hover:border-gray-400"
      )}
    >
      <Icon className="w-5 h-5" />
      <span className="font-medium">{label}</span>
    </button>
  );
}

interface FileUploadAreaProps {
  onFileUpload: (files: FileList) => void;
}

function FileUploadArea({ onFileUpload }: FileUploadAreaProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      onFileUpload(files);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      onFileUpload(files);
    }
  };

  return (
    <div className="mt-8">
      <h3 className="text-lg font-medium text-gray-900 mb-4">上传文本文件</h3>
      
      <div
        className={cn(
          "border-2 border-dashed rounded-lg p-12 text-center transition-colors",
          isDragging 
            ? "border-blue-500 bg-blue-50" 
            : "border-gray-300 bg-gray-50"
        )}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <div className="text-gray-600 mb-2">
          <span className="font-medium">拖拽文件至此</span>
          <span className="mx-2">，或者</span>
          <label className="text-blue-600 font-medium cursor-pointer hover:text-blue-700">
            选择文件
            <input
              type="file"
              className="hidden"
              multiple
              accept=".txt,.md,.mdx,.pdf,.html,.xlsx,.xls,.vtt,.properties,.doc,.docx,.csv,.eml,.msg,.pptx,.xml,.epub,.ppt,.htm"
              onChange={handleFileSelect}
            />
          </label>
        </div>
      </div>

      <div className="mt-4 text-sm text-gray-600">
        <p>已支持 TXT、MARKDOWN、MDX、PDF、HTML、XLSX、XLS、VTT、PROPERTIES、DOC、DOCX、</p>
        <p>CSV、EML、MSG、PPTX、XML、EPUB、PPT、MD、HTM，每个文件不超过 15MB。</p>
      </div>
    </div>
  );
}

export default function Knowledge() {
  const [activeDataSource, setActiveDataSource] = useState<DataSourceType>('text');

  const steps = [
    { label: '选择数据源', step: 1 },
    { label: '文本分段与清洗', step: 2 },
    { label: '处理并完成', step: 3 },
  ];

  const dataSourceOptions = [
    { type: 'text' as DataSourceType, label: '导入已有文本', icon: FileText },
    { type: 'notion' as DataSourceType, label: '同步自 Notion 内容', icon: Database },
    { type: 'web' as DataSourceType, label: '同步自 Web 站点', icon: Globe },
  ];

  const handleFileUpload = (files: FileList) => {
    console.log('Files uploaded:', Array.from(files).map(f => f.name));
    // TODO: 实现文件上传逻辑
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* 面包屑导航 */}
      <div className="flex items-center gap-2 mb-6">
        <button className="flex items-center text-gray-600 hover:text-gray-900">
          <ArrowLeft className="w-4 h-4 mr-1" />
          <span>知识库</span>
        </button>
      </div>

      {/* 步骤指示器 */}
      <StepIndicator currentStep={1} steps={steps} />

      {/* 数据源选择 */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">选择数据源</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {dataSourceOptions.map((option) => (
            <DataSourceTab
              key={option.type}
              type={option.type}
              label={option.label}
              icon={option.icon}
              isActive={activeDataSource === option.type}
              onClick={() => setActiveDataSource(option.type)}
            />
          ))}
        </div>
      </div>

      {/* 根据选择的数据源显示不同内容 */}
      {activeDataSource === 'text' && (
        <FileUploadArea onFileUpload={handleFileUpload} />
      )}

      {activeDataSource === 'notion' && (
        <div className="mt-8 p-8 border border-gray-300 rounded-lg bg-gray-50 text-center">
          <Database className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">连接 Notion</h3>
          <p className="text-gray-600 mb-4">配置 Notion 集成以同步您的内容</p>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            连接 Notion
          </button>
        </div>
      )}

      {activeDataSource === 'web' && (
        <div className="mt-8 p-8 border border-gray-300 rounded-lg bg-gray-50 text-center">
          <Globe className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">同步 Web 站点</h3>
          <p className="text-gray-600 mb-4">输入网站 URL 以抓取和同步内容</p>
          <div className="max-w-md mx-auto">
            <input
              type="url"
              placeholder="https://example.com"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button className="w-full mt-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
              开始同步
            </button>
          </div>
        </div>
      )}
    </div>
  );
}